from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.db import get_session
from domain.service.google_calendar_service import GoogleCalendarService


router = APIRouter(prefix="/google-calendar")


@router.get("/connect/{establishment_id}")
async def get_google_calendar_authorization_url(establishment_id: UUID):
    try:
        authorization_url = GoogleCalendarService.build_authorization_url(establishment_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"authorization_url": authorization_url}


@router.get("/callback")
async def google_calendar_callback(code: str, state: str, db: Session = Depends(get_session)):
    try:
        establishment_id = UUID(state)
        establishment = await GoogleCalendarService.connect_establishment(establishment_id, code, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status": "connected",
        "establishment_id": str(establishment.id),
        "google_calendar_id": establishment.google_calendar_id,
    }


@router.delete("/disconnect/{establishment_id}")
async def google_calendar_disconnect(establishment_id: UUID, db: Session = Depends(get_session)):
    try:
        result = await GoogleCalendarService.disconnect_establishment(establishment_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status": "disconnected",
        "result": result,
    }