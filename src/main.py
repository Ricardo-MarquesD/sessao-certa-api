from fastapi import FastAPI
from config import connection_test
from config import db

app = FastAPI()
connection_test(db)

@app.get("/")
def root():
    return {"message": "Rota raiz"}