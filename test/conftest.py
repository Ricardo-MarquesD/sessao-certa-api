import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def db_session():
    connection = create_engine("mysql+pymysql://root:datachato@localhost:3306/sessao_certa_db")
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()