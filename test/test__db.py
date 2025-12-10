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
    assert result.role == UserRole.ADMIN

def test_plan_table(db_session):
    plans = db_session.query(Plan).all()
    assert len(plans) > 0
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

def test_establishment_table(db_session):
    user = User(
        user_name="Client Establishment",
        password_hash="hashed",
        phone_number="987494321",
        email="establishment@example.com",
        role=UserRole.CLIENT,
        active_status=True
    )
    db_session.add(user)
    db_session.commit()
    user_result = db_session.query(User).filter_by(user_name = "Client Establishment").first()

    client = Client(
        users_id = user_result.id,
        plans_id = 1
    )
    db_session.add(client)
    db_session.commit()
    client_result = db_session.query(Client).filter_by(users_id = client.users_id).first()

    establishment = Establishment(
        clients_id = client_result.id,
        establishment_name = "Test Establishment",
        cnpj = "12345678000199",
        chatbot_phone_number = "1122334455",
        address = "123 Test St",
        due_date = datetime(2024, 12, 31),
        trial_active = True
    )
    db_session.add(establishment)
    db_session.commit()
    
    establishment_result = db_session.query(Establishment).filter_by(establishment_name = "Test Establishment").first()
    assert establishment_result is not None
    assert establishment_result.cnpj == "12345678000199"
    assert establishment_result.clients_id == client_result.id

def test_customer_table(db_session):
    user = User(
        user_name="Customer Line Test",
        password_hash="hashed",
        phone_number="555666777",
        email="customerlinetest@example.com",
        role=UserRole.CLIENT,
        active_status=True
    )
    db_session.add(user)
    db_session.commit()
    user_result = db_session.query(User).filter_by(user_name = "Customer Line Test").first()
    client = Client(
        users_id = user_result.id,
        plans_id = 1
    )
    db_session.add(client)
    db_session.commit()
    client_result = db_session.query(Client).filter_by(users_id = client.users_id).first()
    establishment = Establishment(
        clients_id = client_result.id,
        establishment_name = "Customer Line Establishment",
        cnpj = "98765432000188",
        chatbot_phone_number = "9988776655",
        address = "456 Customer St",
        due_date = datetime(2024, 11, 30),
        trial_active = True
    )
    db_session.add(establishment)
    db_session.commit()
    establishment_result = db_session.query(Establishment).filter_by(establishment_name = "Customer Line Establishment").first()
    customer = Customer(
        establishments_id = establishment_result.id,
        customer_name = "Test Customer",
        phone_number = "555666777"
    )
    db_session.add(customer)
    db_session.commit()
    customer_result = db_session.query(Customer).filter_by(customer_name = "Test Customer").first()
    assert customer_result is not None
    assert customer_result.phone_number == "555666777"
    assert customer_result.establishments_id == establishment_result.id