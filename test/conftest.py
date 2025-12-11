import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    User, UserRole, Plan, TypePlan, Client, Establishment, Customer, Employee, MarketingMessage, Payment, 
    Service, Scheduling,StockProduct, StockMovement
)

@pytest.fixture(scope="session")
def db_session():
    connection = create_engine("mysql+pymysql://root:datachato@localhost:3306/sessao_certa_db")
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

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
    db_session.commit()
    client = Client(
        users_id = user_db.id,
        plans_id = plan_db.id
    )
    yield client, user_db, plan_db

@pytest.fixture(autouse=True)
def clean_db(db_session):
    yield
    db_session.query(Scheduling).delete()
    db_session.query(Customer).delete()
    db_session.query(Service).delete()
    db_session.query(Payment).delete()
    db_session.query(StockMovement).delete()
    db_session.query(StockProduct).delete()
    db_session.query(Payment).delete()
    db_session.query(MarketingMessage).delete()
    db_session.query(Employee).delete()
    db_session.query(Establishment).delete()
    db_session.query(Client).delete()
    db_session.query(User).delete()
    db_session.commit()