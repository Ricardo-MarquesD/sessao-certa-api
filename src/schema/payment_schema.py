from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from utils.enum import PaymentStatus, PaymentType
from domain.entities import Payment
from schema import EstablishmentResponse

class CreatePaymentRequest(BaseModel):
    establishment_id: str
    valor: Decimal = Field(gt=0)
    payment_type: PaymentType
    employee_quantity: int | None = Field(default=None, ge=0)
    gateway_transaction_id: str | None = None

class UpdatePaymentStatusRequest(BaseModel):
    payment_status: PaymentStatus
    gateway_transaction_id: str | None = None

class RefundPaymentRequest(BaseModel):
    reason: str = Field(min_length=10, max_length=500)

class PaymentResponse(BaseModel):
    id: str
    establishment_id: str
    valor: str
    payment_status: str
    payment_type: str
    payment_day: datetime | None
    employee_quantity: int | None
    gateway_transaction_id: str | None
    can_refund: bool
    
    @classmethod
    def from_entity(cls, payment: Payment) -> PaymentResponse:
        return cls(
            id=str(payment.id),
            establishment_id=str(payment.establishment.id),
            valor=str(payment.valor),
            payment_status=payment.payment_status.value,
            payment_type=payment.payment_type.value,
            payment_day=payment.payment_day,
            employee_quantity=payment.employee_quantity,
            gateway_transaction_id=payment.gateway_transaction_id,
            can_refund=payment.can_refund()
        )

class PaymentDetailResponse(BaseModel):
    id: str
    establishment: EstablishmentResponse
    valor: str
    payment_status: str
    payment_type: str
    payment_day: datetime | None
    employee_quantity: int | None
    gateway_transaction_id: str | None
    can_refund: bool
    can_approve: bool
    can_refuse: bool
    
    @classmethod
    def from_entity(cls, payment: Payment) -> PaymentDetailResponse:
        return cls(
            id=str(payment.id),
            establishment=EstablishmentResponse.from_entity(payment.establishment),
            valor=str(payment.valor),
            payment_status=payment.payment_status.value,
            payment_type=payment.payment_type.value,
            payment_day=payment.payment_day,
            employee_quantity=payment.employee_quantity,
            gateway_transaction_id=payment.gateway_transaction_id,
            can_refund=payment.can_refund(),
            can_approve=payment.can_approve(),
            can_refuse=payment.can_refuse()
        )