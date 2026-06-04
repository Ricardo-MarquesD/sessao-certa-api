from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from infra.repository import EstablishmentRepository
from domain.service import WhatsappService
from config.db import get_session
from config import settings
from utils.enum import UserRole
from middleware.auth import require_roles
import aiohttp
from utils.value_object.whatsapp_webhook import WhatsappWebhookHelper

router =  APIRouter(prefix="/whatsapp", tags=["WhatsApp Integration"])

@router.post("/register", dependencies=[Depends(require_roles(UserRole.CLIENT))])
async def register_whatsapp(request: Request, db: Session = Depends(get_session)):
    data = await request.json()

    establishment_id = data.get("establishment_id")
    waba_id = data.get("waba_id")
    phone_number_id = data.get("phone_number_id")
    code = data.get("code")

    if not all([establishment_id, waba_id, phone_number_id, code]):
        raise HTTPException(status_code=400, detail="Dados incompletos no payload")

    repo = EstablishmentRepository(db)
    establishment = repo.get_by_id(establishment_id=establishment_id)
    if not establishment:
        raise HTTPException(status_code=404, detail="Establishment não encontrado")

    try:
        token = await WhatsappService.get_permanent_token(code)
        await WhatsappService.subscribe_webhook(waba_id, token)
    except aiohttp.ClientResponseError as e:
        raise HTTPException(status_code=502, detail=f"Erro na comunicação com a Meta: {e.status}")
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    establishment.waba_id = waba_id
    establishment.chatbot_phone_number = phone_number_id
    establishment.whatsapp_business_token = token
    repo.update(establishment=establishment)

    return {"status": "connected"}


@router.delete("/disconnect/{establishment_id}", dependencies=[Depends(require_roles(UserRole.CLIENT))])
async def disconnect_whatsapp(establishment_id: int, db: Session = Depends(get_session)):
    repo = EstablishmentRepository(db)
    establishment = repo.get_by_id(establishment_id=establishment_id)

    if not establishment:
        raise HTTPException(status_code=404, detail="Establishment não encontrado")

    try:
        if establishment.waba_id and establishment.whatsapp_business_token:
            await WhatsappService.unsubscribe_webhook(establishment.waba_id, establishment.whatsapp_business_token)
    except aiohttp.ClientResponseError as e:
        raise HTTPException(status_code=502, detail=f"Erro na comunicação com a Meta: {e.status}")
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    establishment.waba_id = None
    establishment.chatbot_phone_number = None
    establishment.whatsapp_business_token = None
    repo.update(establishment=establishment)

    return {"status": "disconnected"}

@router.get("/webhook")
async def webhook_verification(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    if hub_mode == "subscribe" and hub_verify_token == settings.webhook_verify_token:
        print(hub_verify_token)
        return PlainTextResponse(hub_challenge, status_code=200)
    raise HTTPException(403, "Token de verificação inválido")

@router.post("/webhook")
async def webhook_post(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()

    background_tasks.add_task(WhatsappWebhookHelper.enqueue_process_message, data)

    return {"status": "ok"}