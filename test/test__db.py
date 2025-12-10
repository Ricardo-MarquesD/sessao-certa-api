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

def test_plan_table(db_session):
    plans = db_session.query(Plan).all()
    for plan in plans:
        assert plan.type_plan in TypePlan

def test_client_table(db_session):
    user = User(
            user_name="Client User",
            password_hash="hashed",
            phone_number="987654321",
            email="client@example.com",
            role=UserRole.CLIENT,
            active_status=True
        )
    db_session.add(user)
    db_session.commit()

    user_result = db_session.query(User).filter_by(user_name = "Client User").first()
    client = Client(users_id = user_result.id, plans_id = 1)
    db_session.add(client)
    db_session.commit()

    client_result = db_session.query(Client).filter_by(users_id = client.users_id).first()
    assert client_result.plans_id == 1
    assert client_result.users_id == user_result.id