from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from controller.appointments_controller import router as appointments_router
from controller.auth_controller import router as auth_router
from controller.employee_controller import router as employee_router
from controller.establishment_controller import router as establishment_router
from controller.google_calendar_controller import router as google_calendar_router
from controller.image_controller import router as image_router
from controller.payment_webhook_controller import router as payment_webhook_router
from controller.user_controller import router as user_router
from controller.whatsapp_controller import router as whatsapp_router
from middleware.auth import AuthError
from schema import ErrorResponse

app = FastAPI(title="API da SessãoCerta", version="1.0.0")

img_dir = Path(__file__).resolve().parent / "src" / "img"
app.mount("/img", StaticFiles(directory=img_dir), name="img")

app.include_router(whatsapp_router)
app.include_router(appointments_router)
app.include_router(employee_router)
app.include_router(establishment_router)
app.include_router(google_calendar_router)
app.include_router(image_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(payment_webhook_router)


@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    payload = ErrorResponse(error=exc.error, detail=exc.detail)
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(payload))

@app.get("/")
def root():
    return {"message": "Rota raiz"}