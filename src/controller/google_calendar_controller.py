from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.db import get_session
from domain.service.google_calendar_service import GoogleCalendarService
from infra.google_calendar import GoogleCalendarClientFactory, get_google_calendar_client_factory


router = APIRouter(prefix="/google-calendar")


def get_google_calendar_service(
    factory: GoogleCalendarClientFactory = Depends(get_google_calendar_client_factory),
) -> GoogleCalendarService:
    return GoogleCalendarService(factory)


@router.get("/connect/{establishment_id}")
async def get_google_calendar_authorization_url(
    establishment_id: UUID,
    service: GoogleCalendarService = Depends(get_google_calendar_service),
):
    try:
        authorization_url = service.build_authorization_url(establishment_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"authorization_url": authorization_url}


@router.get("/callback")
async def google_calendar_callback(
    code: str,
    state: str,
    db: Session = Depends(get_session),
    service: GoogleCalendarService = Depends(get_google_calendar_service),
):
    try:
        establishment_id = UUID(state)
        establishment = await service.connect_establishment(establishment_id, code, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status": "connected",
        "establishment_id": str(establishment.id),
        "google_calendar_id": establishment.google_calendar_id,
    }


@router.delete("/disconnect/{establishment_id}")
async def google_calendar_disconnect(
    establishment_id: UUID,
    db: Session = Depends(get_session),
    service: GoogleCalendarService = Depends(get_google_calendar_service),
):
    try:
        result = await service.disconnect_establishment(establishment_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status": "disconnected",
        "result": result,
    }