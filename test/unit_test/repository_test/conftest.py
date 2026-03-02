import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from decimal import Decimal
from utils.enum import UserRole, TypePlan, PaymentStatus, PaymentType, AppointmentStatus, MovementType
from infra.models import (
    UserModel,
    PlanModel,
    ClientModel,
    EstablishmentModel,
    CustomerModel,
    EmployeeModel,
    ServiceModel,
    PaymentModel,
    SchedulingModel,
    MarketingMessageModel,
    StockProductModel,
    StockMovementModel
)

@pytest.fixture(scope="function")
def db_session():
    """Cria uma sessão de banco de dados para testes"""
    connection = create_engine("mysql+pymysql://root:datachato@localhost:3306/sessao_certa_db")
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def sample_user(db_session):
    """Cria um usuário de exemplo no banco"""
    user = UserModel(
        user_name="Test User",
        password_hash="hashed_password_123",
        phone_number="11987654321",
        email="testuser@example.com",
        img_url="/uploads/test.png",
        role=UserRole.CLIENT,
        active_status=True
    )
    db_session.add(user)
    db_session.flush()
    
    yield user
    
    # Cleanup é feito pelo rollback do db_session


@pytest.fixture(scope="function")
def sample_plan(db_session):
    """Cria um plano de exemplo no banco"""
    plan = PlanModel(
        type_plan=TypePlan.SILVER,
        basic_price=Decimal("49.90"),
        max_employee=5,
        allow_stock=True,
        allow_advanced_analysis=True
    )
    db_session.add(plan)
    db_session.flush()
    
    yield plan


@pytest.fixture(scope="function")
def sample_client(db_session, sample_user, sample_plan):
    """Cria um cliente de exemplo no banco"""
    client = ClientModel(
        users_id=sample_user.id,
        plans_id=sample_plan.id
    )
    db_session.add(client)
    db_session.flush()
    
    yield client


@pytest.fixture(scope="function")
def sample_establishment(db_session, sample_client):
    """Cria um estabelecimento de exemplo no banco"""
    establishment = EstablishmentModel(
        clients_id=sample_client.id,
        waba_id="WABA-TEST-001",
        whatsapp_business_token="whatsapp-token-test-001",
        establishment_name="Salão Teste",
        cnpj="12345678901234",
        chatbot_phone_number="11987654321",
        address="Rua Teste, 123",
        img_url="/uploads/salao.png",
        due_date=datetime(2026, 12, 31),
        trial_active=False
    )
    db_session.add(establishment)
    db_session.flush()
    
    yield establishment


@pytest.fixture(scope="function")
def sample_customer(db_session, sample_establishment):
    """Cria um cliente (customer) de exemplo no banco"""
    customer = CustomerModel(
        customer_name="Cliente Teste",
        phone_number="11999998888",
        establishments_id=sample_establishment.id
    )
    db_session.add(customer)
    db_session.flush()
    
    yield customer


@pytest.fixture(scope="function")
def sample_employee_user(db_session):
    """Cria um usuário funcionário de exemplo no banco"""
    user = UserModel(
        user_name="Funcionário Teste",
        password_hash="hashed_password_456",
        phone_number="11977776666",
        email="employee@example.com",
        img_url="/uploads/employee.png",
        role=UserRole.EMPLOYEE,
        active_status=True
    )
    db_session.add(user)
    db_session.flush()
    
    yield user


@pytest.fixture(scope="function")
def sample_employee(db_session, sample_employee_user, sample_establishment):
    """Cria um funcionário de exemplo no banco"""
    employee = EmployeeModel(
        users_id=sample_employee_user.id,
        establishments_id=sample_establishment.id,
        percentage_commission=Decimal("10.00"),
        available_hours={"monday": ["09:00-18:00"], "tuesday": ["09:00-18:00"]}
    )
    db_session.add(employee)
    db_session.flush()
    
    yield employee


@pytest.fixture(scope="function")
def sample_service(db_session, sample_establishment):
    """Cria um serviço de exemplo no banco"""
    service = ServiceModel(
        establishments_id=sample_establishment.id,
        service_name="Corte de Cabelo",
        description_service="Corte tradicional",
        time_duration=30,
        price=Decimal("50.00"),
        active=True
    )
    db_session.add(service)
    db_session.flush()
    
    yield service


@pytest.fixture(scope="function")
def sample_payment(db_session, sample_establishment):
    """Cria um pagamento de exemplo no banco"""
    payment = PaymentModel(
        establishments_id=sample_establishment.id,
        valor=Decimal("99.90"),
        payment_day=datetime(2026, 1, 15),
        payment_status=PaymentStatus.PENDING,
        payment_type=PaymentType.MONTHLY_SUBSCRIPTION,
        employee_quantity=3,
        gateway_transaction_id="TXN123456"
    )
    db_session.add(payment)
    db_session.flush()
    
    yield payment


@pytest.fixture(scope="function")
def sample_scheduling(db_session, sample_establishment, sample_employee, sample_customer, sample_service):
    """Cria um agendamento de exemplo no banco"""
    scheduling = SchedulingModel(
        establishments_id=sample_establishment.id,
        employees_id=sample_employee.id,
        customers_id=sample_customer.id,
        services_id=sample_service.id,
        appointment_date=datetime(2027, 6, 15, 14, 0),
        appointment_status=AppointmentStatus.SCHEDULED,
        notification_sent=False
    )
    db_session.add(scheduling)
    db_session.flush()
    
    yield scheduling


@pytest.fixture(scope="function")
def sample_marketing_message(db_session, sample_establishment):
    """Cria uma mensagem de marketing de exemplo no banco"""
    message = MarketingMessageModel(
        establishments_id=sample_establishment.id,
        title="Promoção Especial",
        content="Aproveite 20% de desconto nesta semana!"
    )
    db_session.add(message)
    db_session.flush()
    
    yield message


@pytest.fixture(scope="function")
def sample_stock_product(db_session, sample_establishment):
    """Cria um produto de estoque de exemplo no banco"""
    product = StockProductModel(
        establishments_id=sample_establishment.id,
        product_name="Shampoo Premium",
        quantity=50,
        price=Decimal("25.90")
    )
    db_session.add(product)
    db_session.flush()
    
    yield product


@pytest.fixture(scope="function")
def sample_stock_movement(db_session, sample_stock_product):
    """Cria uma movimentação de estoque de exemplo no banco"""
    movement = StockMovementModel(
        stock_products_id=sample_stock_product.id,
        movement_type=MovementType.INPUT,
        quantity=20
    )
    db_session.add(movement)
    db_session.flush()
    
    yield movement
