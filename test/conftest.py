import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    AppointmentStatus,
    Client,
    Customer,
    Employee,
    Establishment,
    MarketingMessage,
    MovementType,
    Payment,
    PaymentStatus,
    PaymentType,
    Plan,
    Scheduling,
    Service,
    StockMovement,
    StockProduct,
    TypePlan,
    User,
    UserRole,
)

@pytest.fixture(scope="function")
def db_session():
    connection = create_engine("mysql+pymysql://root:datachato@localhost:3306/sessao_certa_db")
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def user_db():
    user = User(
        user_name = "Test User",
        password_hash = "hash password",
        phone_number = "5561912341234",
        email = "test@example.com",
        role = UserRole.ADMIN,
        active_status = True
    )
    yield user

@pytest.fixture(scope="function")
def plan_db():
    plan = Plan(
        type_plan = TypePlan.SILVER,
        basic_price = 15.90,
        max_employee = 3,
        allow_stock = False,
        allow_advanced_analysis = True
    )
    yield plan

@pytest.fixture(scope="function")
def client_db(db_session ,user_db, plan_db):
    db_session.add(user_db)
    db_session.add(plan_db)
    db_session.flush()
    client = Client(
        users_id = user_db.id,
        plans_id = plan_db.id
    )
    yield client, user_db, plan_db

@pytest.fixture(scope="function")
def establishment_db(db_session, client_db):
    client, _, _ = client_db
    db_session.add(client)
    db_session.flush()

    establishment = Establishment(
        clients_id = client.id,
        establishment_name = "Test Establishment",
        cnpj = "12123123000122",
        chatbot_phone_number = "5521990032455",
        address = "Avenida Test Rua Test 1",
        due_date = datetime(2030, 2, 11),
        trial_active = False
    )
    yield establishment, client

@pytest.fixture(scope="function")
def customer_db(db_session, establishment_db):
    establishment, _ = establishment_db
    db_session.add(establishment)
    db_session.flush()

    customer = Customer(
        customer_name = "Test Customer",
        phone_number = "5511980657662",
        establishments_id = establishment.id
    )
    yield customer, establishment

@pytest.fixture(scope="function")
def employee_db(db_session, user_db, establishment_db):
    establishment, _ = establishment_db
    db_session.add(user_db)
    db_session.add(establishment)
    db_session.flush()

    employee = Employee(
        users_id = user_db.id,
        establishments_id = establishment.id,
        percentage_commission = 0.07,
        available_hours = {"hour_able": "10:00am - 4:00pm", "days_able": "Monday - Friday"}
    )
    yield employee, user_db, establishment

@pytest.fixture(scope="function")
def marketing_db(db_session, establishment_db):
    establishment, _ = establishment_db
    db_session.add(establishment)
    db_session.flush()

    marketing_message = MarketingMessage(
        establishments_id = establishment.id,
        title = "Tittle Test",
        content = "Content Test"
    )
    yield marketing_message, establishment

@pytest.fixture(scope="function")
def payment_db(db_session, establishment_db):
    establishment, _ = establishment_db
    db_session.add(establishment)
    db_session.flush()

    payment = Payment(
        establishments_id = establishment.id,
        valor = 99.90,
        payment_day = datetime(2030, 1, 1, 10, 0, 0),
        payment_status = PaymentStatus.PENDING,
        payment_type = PaymentType.MONTHLY_SUBSCRIPTION,
        employee_quantity = 5,
        gateway_transaction_id = "GTX123456"
    )
    yield payment, establishment

@pytest.fixture(scope="function")
def stock_product_db(db_session, establishment_db):
    establishment, _ = establishment_db
    db_session.add(establishment)
    db_session.flush()

    stock_product = StockProduct(
        establishments_id=establishment.id,
        product_name="Test Product",
        quantity=100,
        price=25.50
    )
    yield stock_product, establishment

@pytest.fixture(scope="function")
def stock_movement_db(db_session, stock_product_db):
    stock_product, establishment = stock_product_db
    db_session.add(stock_product)
    db_session.flush()

    stock_movement = StockMovement(
        stock_products_id=stock_product.id,
        movement_type=MovementType.INPUT,
        quantity=50,
        date=datetime(2030, 1, 2, 15, 0, 0)
    )
    yield stock_movement, stock_product, establishment

@pytest.fixture(scope="function")
def service_db(db_session, establishment_db):
    establishment, _ = establishment_db
    db_session.add(establishment)
    db_session.flush()

    service = Service(
        establishments_id=establishment.id,
        service_name="Test Service",
        description_service="Test Description",
        time_duration=30,
        price=50.00,
        active=True
    )
    yield service, establishment

@pytest.fixture(scope="function")
def scheduling_db(db_session, establishment_db, employee_db, customer_db, service_db):
    establishment, _ = establishment_db
    employee, _, _ = employee_db
    customer, _ = customer_db
    service, _ = service_db
    db_session.add_all([establishment, employee, customer, service])
    db_session.flush()

    scheduling = Scheduling(
        establishments_id=establishment.id,
        employees_id=employee.id,
        customers_id=customer.id,
        services_id=service.id,
        appointment_date=datetime(2030, 3, 10, 14, 0, 0),
        appointment_status=AppointmentStatus.SCHEDULED,
        notification_sent=False
    )
    yield scheduling, establishment, employee, customer, service