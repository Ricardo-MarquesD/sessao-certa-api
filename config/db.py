from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings

url_conn = f"mysql+pymysql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_database}"
engine = create_engine(
    url_conn,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def connection_test(engine):
    try:
        print("Conectando...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Banco de dados conectado.")
    except Exception as e:
        print(f"Falha ao conectar banco de dados: {e}")

def get_session():
    session = Session()
    try:
        yield session
        session.commit()  # Commit automático se não houver exceção
    except Exception:
        session.rollback()  # Rollback em caso de erro
        raise
    finally:
        session.close()