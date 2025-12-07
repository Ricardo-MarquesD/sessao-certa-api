from fastapi import FastAPI
from config import connection_test
from config import engine

app = FastAPI()
connection_test(engine)

@app.get("/")
def root():
    return {"message": "Rota raiz"}