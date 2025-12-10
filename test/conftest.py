import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    User, Client, Establishment, Customer, Employee, MarketingMessage, Payment, 
    Service, Scheduling,StockProduct, StockMovement
)

@pytest.fixture(scope="session")
def db_session():
    connection = create_engine("mysql+pymysql://root:datachato@localhost:3306/sessao_certa_db")
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()

@pytest.fixture(autouse=True)
def clean_db(db_session):
    yield
    #db_session.query(Scheduling).delete()
    #db_session.query(Customer).delete()
    #db_session.query(Service).delete()
    #db_session.query(Payment).delete()
    #db_session.query(StockMovement).delete()
    #db_session.query(StockProduct).delete()
    #db_session.query(Payment).delete()
    #db_session.query(MarketingMessage).delete()
    #db_session.query(Employee).delete()
    #db_session.query(Establishment).delete()
    db_session.query(Client).delete()
    db_session.query(User).delete()
    db_session.commit()