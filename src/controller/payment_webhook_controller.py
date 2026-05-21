from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from config.db import get_session
from middleware.auth import get_current_user, require_roles
from utils.enum import UserRole
from utils.value_object.stripe_webhook import StripeWebhookHelper

router = APIRouter(prefix="/stripe", tags=["Payment Integration"])


@router.post("/portal", status_code=status.HTTP_200_OK, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def create_billing_portal(
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> dict[str, str]:
    url = StripeWebhookHelper.create_billing_portal_url(db=db, user_id=current_user.id)
    return {"url": url}


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request, db: Session = Depends(get_session)) -> dict[str, str]:
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    event = StripeWebhookHelper.construct_event(payload, sig_header)
    return StripeWebhookHelper.handle_event(event, db)
