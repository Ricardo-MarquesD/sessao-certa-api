from sqlalchemy import text, create_engine
from config.settings import settings

url_conn = f"mysql+pymysql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_database}"
print(url_conn)
db = create_engine(url_conn)

def connection_test(db):
    try:
        print("Conectando...")
        with db.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Banco de dados conectado.")
    except Exception as e:
        print(f"Falha ao conectar banco de dados: {e}")