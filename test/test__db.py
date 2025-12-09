import pytest
from datetime import datetime
from models import (
    User, UserRole, Plan, TypePlan, Client, Establishment, Customer, Employee,
    MarketingMessage, Payment, PaymentType, PaymentStatus, Service, Scheduling,
    AppointmentStatus, StockProduct, StockMovement, MovementType
)

def test_user_table(db_session):
    user = User(
        user_name = "Test User",
        password_hash = "hashed_passwod",
        phone_number = "123456789",
        email = "test@example.com",
        role = UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    result = db_session.query(User).filter_by(user_name = "Test User").first()
    assert result is not None
    assert result.user_name == "Test User"