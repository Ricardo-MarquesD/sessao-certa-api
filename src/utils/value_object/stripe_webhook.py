from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from domain.entities import Payment
from infra.repository import ClientRepository, EstablishmentRepository, PaymentRepository, UserRepository
from utils.enum import PaymentStatus, PaymentType

stripe.api_key = settings.stripe_api_key


class StripeWebhookHelper:

    @staticmethod
    def create_billing_portal_url(*, db: Session, user_id) -> str:
        if not settings.stripe_success_url:
            raise HTTPException(status_code=500, detail="STRIPE_SUCCESS_URL is required")

        client_repo = ClientRepository(db)
        client = client_repo.get_by_user_id(user_id)
        if client is None or not client.stripe_customer_id:
            raise HTTPException(status_code=404, detail="Stripe customer not found")

        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=client.stripe_customer_id,
                return_url=settings.stripe_success_url,
            )
        except stripe.error.StripeError as exc:
            message = getattr(exc, "user_message", None) or str(exc)
            raise HTTPException(status_code=400, detail=message) from exc

        return str(portal_session.url)

    @staticmethod
    def construct_event(payload: bytes, sig_header: str | None) -> dict[str, Any]:
        if not settings.stripe_webhook_secret_instant:
            raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

        try:
            return stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.stripe_webhook_secret_instant,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid payload") from exc
        except stripe.error.SignatureVerificationError as exc:
            raise HTTPException(status_code=400, detail="Invalid signature") from exc

    @staticmethod
    def handle_event(event: dict[str, Any], db: Session) -> dict[str, str]:
        event_type = event.get("type")
        data_object = event.get("data", {}).get("object", {})

        if event_type == "invoice.paid":
            return StripeWebhookHelper._handle_invoice_event(data_object, success=True, db=db)
        if event_type == "invoice.payment_failed":
            return StripeWebhookHelper._handle_invoice_event(data_object, success=False, db=db)
        if event_type == "checkout.session.async_payment_succeeded":
            return StripeWebhookHelper._handle_session_event(data_object, success=True, db=db)
        if event_type == "checkout.session.async_payment_failed":
            return StripeWebhookHelper._handle_session_event(data_object, success=False, db=db)
        if event_type == "customer.subscription.deleted":
            return StripeWebhookHelper._handle_subscription_event(data_object, canceled=True, db=db)
        if event_type == "customer.subscription.updated":
            return StripeWebhookHelper._handle_subscription_event(data_object, canceled=False, db=db)

        return {"status": "ignored"}

    @staticmethod
    def _amount_to_decimal(amount: int | None) -> Decimal | None:
        if amount is None:
            return None
        return Decimal(str(amount)) / Decimal("100")

    @staticmethod
    def _normalize_interval(interval: str | None) -> PaymentType:
        if interval == "year":
            return PaymentType.ANNUAL_SUBSCRIPTION
        return PaymentType.MONTHLY_SUBSCRIPTION

    @staticmethod
    def _normalize_billing_cycle(cycle: str | None) -> PaymentType:
        normalized = (cycle or "").strip().lower()
        if normalized in {"anualmente", "anual", "annual", "yearly", "year"}:
            return PaymentType.ANNUAL_SUBSCRIPTION
        return PaymentType.MONTHLY_SUBSCRIPTION

    @staticmethod
    def _get_invoice_line(invoice: dict[str, Any]) -> dict[str, Any] | None:
        lines = invoice.get("lines", {}).get("data", [])
        return lines[0] if lines else None

    @staticmethod
    def _get_period_end_from_invoice(invoice: dict[str, Any]) -> datetime | None:
        line = StripeWebhookHelper._get_invoice_line(invoice)
        period_end = None
        if line:
            period = line.get("period", {})
            period_end = period.get("end")
        if not period_end:
            period_end = invoice.get("period_end")
        if not period_end:
            return None
        return datetime.fromtimestamp(int(period_end))

    @staticmethod
    def _resolve_invoice_from_session(session: dict[str, Any]) -> dict[str, Any] | None:
        invoice_id = session.get("invoice")
        if invoice_id:
            return stripe.Invoice.retrieve(invoice_id)

        subscription_id = session.get("subscription")
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            latest_invoice_id = subscription.get("latest_invoice")
            if latest_invoice_id:
                return stripe.Invoice.retrieve(latest_invoice_id)

        return None

    @staticmethod
    def _payment_type_from_invoice(invoice: dict[str, Any]) -> PaymentType:
        line = StripeWebhookHelper._get_invoice_line(invoice)
        interval = None
        if line:
            price = line.get("price", {})
            recurring = price.get("recurring") if isinstance(price, dict) else None
            if isinstance(recurring, dict):
                interval = recurring.get("interval")
        return StripeWebhookHelper._normalize_interval(interval)

    @staticmethod
    def _payment_amount_from_invoice(invoice: dict[str, Any]) -> int | None:
        for key in ("amount_paid", "amount_due", "amount_remaining", "amount_total"):
            value = invoice.get(key)
            if value:
                return int(value)
        return None

    @staticmethod
    def _payment_amount_from_session(session: dict[str, Any]) -> int | None:
        amount_total = session.get("amount_total")
        return int(amount_total) if amount_total else None

    @staticmethod
    def _fallback_amount(client, employee_quantity: int | None, payment_type: PaymentType) -> Decimal:
        count = employee_quantity or 1
        base = client.plan.calculate_total_price(count)
        if payment_type == PaymentType.ANNUAL_SUBSCRIPTION:
            return base * Decimal("12")
        return base

    @staticmethod
    def _upsert_payment(
        payment_repo: PaymentRepository,
        *,
        establishment,
        amount_decimal: Decimal,
        payment_status: PaymentStatus,
        payment_type: PaymentType,
        employee_quantity: int | None,
        gateway_transaction_id: str,
    ) -> Payment:
        existing = payment_repo.get_by_gateway_transaction_id(gateway_transaction_id)
        payment_day = datetime.utcnow()

        if existing:
            existing.valor = amount_decimal
            existing.payment_day = payment_day
            existing.payment_status = payment_status
            existing.payment_type = payment_type
            existing.employee_quantity = employee_quantity
            existing.gateway_transaction_id = gateway_transaction_id
            return payment_repo.update(existing)

        payment = Payment(
            id=None,
            establishment=establishment,
            valor=amount_decimal,
            payment_day=payment_day,
            payment_status=payment_status,
            payment_type=payment_type,
            employee_quantity=employee_quantity,
            gateway_transaction_id=gateway_transaction_id,
        )
        return payment_repo.create(payment)

    @staticmethod
    def _handle_invoice_event(invoice: dict[str, Any], *, success: bool, db: Session) -> dict[str, str]:
        customer_id = invoice.get("customer")
        if not customer_id:
            return {"status": "ignored"}

        client_repo = ClientRepository(db)
        client = client_repo.get_by_stripe_customer_id(str(customer_id))
        if client is None:
            return {"status": "ignored"}

        establishment_repo = EstablishmentRepository(db)
        establishment = establishment_repo.get_by_client_id(client.id)
        if establishment is None:
            return {"status": "ignored"}

        user_repo = UserRepository(db)
        user = user_repo.get_by_id(client.user.id)
        if user is None:
            return {"status": "ignored"}

        was_active = user.is_active()
        subscription_id = invoice.get("subscription")
        period_end = StripeWebhookHelper._get_period_end_from_invoice(invoice)
        payment_type = StripeWebhookHelper._payment_type_from_invoice(invoice)
        line = StripeWebhookHelper._get_invoice_line(invoice)
        employee_quantity = line.get("quantity") if line else None
        amount_value = StripeWebhookHelper._payment_amount_from_invoice(invoice)
        amount_decimal = StripeWebhookHelper._amount_to_decimal(amount_value)
        if amount_decimal is None or amount_decimal <= 0:
            amount_decimal = StripeWebhookHelper._fallback_amount(client, employee_quantity, payment_type)

        payment_repo = PaymentRepository(db)
        gateway_transaction_id = str(invoice.get("id") or subscription_id or "")
        if not gateway_transaction_id:
            return {"status": "ignored"}

        if success:
            user.active_status = True
            user_repo.update(user)

            if subscription_id:
                establishment.stripe_subscription_id = str(subscription_id)
            if period_end:
                establishment.due_date = period_end
            establishment.trial_active = False
            establishment_repo.update(establishment)

            StripeWebhookHelper._upsert_payment(
                payment_repo,
                establishment=establishment,
                amount_decimal=amount_decimal,
                payment_status=PaymentStatus.APPROVED,
                payment_type=payment_type,
                employee_quantity=employee_quantity,
                gateway_transaction_id=gateway_transaction_id,
            )
            return {"status": "processed"}

        StripeWebhookHelper._upsert_payment(
            payment_repo,
            establishment=establishment,
            amount_decimal=amount_decimal,
            payment_status=PaymentStatus.REFUSED,
            payment_type=payment_type,
            employee_quantity=employee_quantity,
            gateway_transaction_id=gateway_transaction_id,
        )

        if was_active:
            establishment.due_date = datetime.utcnow() + timedelta(days=7)
            establishment_repo.update(establishment)

        return {"status": "processed"}

    @staticmethod
    def _handle_session_event(session: dict[str, Any], *, success: bool, db: Session) -> dict[str, str]:
        invoice = StripeWebhookHelper._resolve_invoice_from_session(session)
        if invoice:
            return StripeWebhookHelper._handle_invoice_event(invoice, success=success, db=db)

        customer_id = session.get("customer")
        if not customer_id:
            return {"status": "ignored"}

        client_repo = ClientRepository(db)
        client = client_repo.get_by_stripe_customer_id(str(customer_id))
        if client is None:
            return {"status": "ignored"}

        establishment_repo = EstablishmentRepository(db)
        establishment = establishment_repo.get_by_client_id(client.id)
        if establishment is None:
            return {"status": "ignored"}

        user_repo = UserRepository(db)
        user = user_repo.get_by_id(client.user.id)
        if user is None:
            return {"status": "ignored"}

        was_active = user.is_active()
        subscription_id = session.get("subscription")
        payment_type = StripeWebhookHelper._normalize_billing_cycle((session.get("metadata") or {}).get("billing_cycle"))
        employee_quantity = (session.get("metadata") or {}).get("employee_count")
        employee_quantity = int(employee_quantity) if employee_quantity else None
        amount_value = StripeWebhookHelper._payment_amount_from_session(session)
        amount_decimal = StripeWebhookHelper._amount_to_decimal(amount_value)
        if amount_decimal is None or amount_decimal <= 0:
            amount_decimal = StripeWebhookHelper._fallback_amount(client, employee_quantity, payment_type)

        gateway_transaction_id = str(session.get("invoice") or session.get("id") or "")
        if not gateway_transaction_id:
            return {"status": "ignored"}

        payment_repo = PaymentRepository(db)

        if success:
            user.active_status = True
            user_repo.update(user)

            if subscription_id:
                establishment.stripe_subscription_id = str(subscription_id)
                subscription = stripe.Subscription.retrieve(subscription_id)
                period_end = subscription.get("current_period_end")
                if period_end:
                    establishment.due_date = datetime.fromtimestamp(int(period_end))
            establishment.trial_active = False
            establishment_repo.update(establishment)

            StripeWebhookHelper._upsert_payment(
                payment_repo,
                establishment=establishment,
                amount_decimal=amount_decimal,
                payment_status=PaymentStatus.APPROVED,
                payment_type=payment_type,
                employee_quantity=employee_quantity,
                gateway_transaction_id=gateway_transaction_id,
            )
            return {"status": "processed"}

        StripeWebhookHelper._upsert_payment(
            payment_repo,
            establishment=establishment,
            amount_decimal=amount_decimal,
            payment_status=PaymentStatus.REFUSED,
            payment_type=payment_type,
            employee_quantity=employee_quantity,
            gateway_transaction_id=gateway_transaction_id,
        )

        if was_active:
            establishment.due_date = datetime.utcnow() + timedelta(days=7)
            establishment_repo.update(establishment)

        return {"status": "processed"}

    @staticmethod
    def _handle_subscription_event(subscription: dict[str, Any], *, canceled: bool, db: Session) -> dict[str, str]:
        customer_id = subscription.get("customer")
        if not customer_id:
            return {"status": "ignored"}

        client_repo = ClientRepository(db)
        client = client_repo.get_by_stripe_customer_id(str(customer_id))
        if client is None:
            return {"status": "ignored"}

        establishment_repo = EstablishmentRepository(db)
        establishment = establishment_repo.get_by_client_id(client.id)
        if establishment is None:
            return {"status": "ignored"}

        period_end = subscription.get("current_period_end")
        period_end_dt = datetime.fromtimestamp(int(period_end)) if period_end else None
        if period_end_dt:
            establishment.due_date = period_end_dt
            establishment_repo.update(establishment)

        if canceled:
            return {"status": "processed"}

        cancel_at_period_end = subscription.get("cancel_at_period_end")
        if cancel_at_period_end:
            return {"status": "processed"}

        return {"status": "ignored"}
