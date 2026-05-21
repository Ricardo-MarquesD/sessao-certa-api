from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import stripe

from config.settings import settings
from domain.entities import Plan
from utils.enum import TypePlan


@dataclass
class CheckoutSessionResult:
    url: str
    session_id: str


class StripeService:
    def __init__(self) -> None:
        stripe.api_key = settings.stripe_api_key
        if not settings.stripe_api_key:
            raise ValueError("STRIPE_API_KEY is required")
        if not settings.stripe_product_id:
            raise ValueError("STRIPE_PRODUCT_ID is required")

    @staticmethod
    def _normalize_cycle(value: str) -> str:
        normalized = (value or "").strip().lower()
        if normalized in {"mensalmente", "mensal", "monthly"}:
            return "monthly"
        if normalized in {"anualmente", "anual", "yearly", "annual"}:
            return "annual"
        raise ValueError("Invalid billing_cycle, use Mensalmente or Anualmente")

    @staticmethod
    def _price_id(plan_type: TypePlan, cycle: str) -> str:
        if cycle == "annual":
            mapping = {
                TypePlan.BRONZE: settings.stripe_price_id_annual_bronze,
                TypePlan.SILVER: settings.stripe_price_id_annual_silver,
                TypePlan.GOLD: settings.stripe_price_id_annual_gold,
            }
        else:
            mapping = {
                TypePlan.BRONZE: settings.stripe_price_id_monthly_bronze,
                TypePlan.SILVER: settings.stripe_price_id_monthly_silver,
                TypePlan.GOLD: settings.stripe_price_id_monthly_gold,
            }
        price_id = mapping.get(plan_type, "")
        if not price_id:
            raise ValueError("Price id not configured")
        return price_id

    def create_customer(self, *, email: str, name: str) -> str:
        customer = stripe.Customer.create(email=email, name=name)
        return str(customer.get("id"))

    def create_checkout_session(
        self,
        *,
        customer_id: str,
        plan: Plan,
        employee_count: int,
        billing_cycle: str,
        metadata: dict[str, Any],
    ) -> CheckoutSessionResult:
        cycle = self._normalize_cycle(billing_cycle)
        if not settings.stripe_success_url or not settings.stripe_cancel_url:
            raise ValueError("STRIPE_SUCCESS_URL and STRIPE_CANCEL_URL are required")
        if employee_count < 1:
            raise ValueError("employee_count must be at least 1")

        payment_methods = [
            method.strip()
            for method in (settings.stripe_payment_methods or "").split(",")
            if method.strip()
        ]
        if not payment_methods:
            raise ValueError("STRIPE_PAYMENT_METHODS is required")
        price_id = self._price_id(plan.type_plan, cycle)

        line_items = [
            {
                "price": price_id,
                "quantity": employee_count,
            }
        ]

        discounts = None
        if cycle == "annual":
            if not settings.stripe_coupon_annual:
                raise ValueError("STRIPE_COUPON_ANNUAL is required for annual billing")
            discounts = [{"coupon": settings.stripe_coupon_annual}]

        try:
            session = stripe.checkout.Session.create(
                mode="subscription",
                customer=customer_id,
                line_items=line_items,
                success_url=settings.stripe_success_url,
                cancel_url=settings.stripe_cancel_url,
                metadata={k: str(v) for k, v in (metadata or {}).items()},
                discounts=discounts,
                payment_method_types=payment_methods,
            )
        except stripe.error.StripeError as exc:
            message = getattr(exc, "user_message", None) or str(exc)
            raise ValueError(message) from exc

        return CheckoutSessionResult(url=str(session.url), session_id=str(session.id))
