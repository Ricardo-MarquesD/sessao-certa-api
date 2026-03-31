from fastapi import FastAPI
from controller.appointments_controller import router as appointments_router
from controller.google_calendar_controller import router as google_calendar_router
from controller.whatsapp_controller import router as whatsapp_router

app = FastAPI()

app.include_router(whatsapp_router)
app.include_router(appointments_router)
app.include_router(google_calendar_router)

@app.get("/")
def root():
    return {"message": "Rota raiz"}