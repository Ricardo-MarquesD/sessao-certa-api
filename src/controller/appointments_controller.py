from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from config.db import get_session
from domain.service import AppointmentsService
from utils.enum import UserRole
from middleware.auth import require_roles
from schema import (
    CreateSchedulingRequest,
    DeleteResponse,
    SchedulingCalendarResponse,
    SchedulingDetailResponse,
    SchedulingResponse,
    UpdateSchedulingRequest,
)

router = APIRouter(prefix="/appointments")

@router.get("", response_model=list[SchedulingCalendarResponse], dependencies=[Depends(require_roles(UserRole.CLIENT, UserRole.EMPLOYEE))])
def list_appointments(
    establishment_id: UUID = Query(...),
    cursor: str | None = None,
    limit: int = Query(default=15, ge=1, le=100),
    db: Session = Depends(get_session),
):
    try:
        schedulings = AppointmentsService.list_appointments(db=db, establishment_id=establishment_id, cursor=cursor, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return [SchedulingCalendarResponse.from_entity(scheduling) for scheduling in schedulings]


@router.get("/{scheduling_id}", response_model=SchedulingDetailResponse, dependencies=[Depends(require_roles(UserRole.CLIENT, UserRole.EMPLOYEE))])
def get_appointment(scheduling_id: UUID, db: Session = Depends(get_session)):
    try:
        scheduling = AppointmentsService.get_appointment(db=db, scheduling_id=scheduling_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return SchedulingDetailResponse.from_entity(scheduling)


@router.post("", response_model=SchedulingResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.CLIENT, UserRole.EMPLOYEE))])
def create_appointment(payload: CreateSchedulingRequest, db: Session = Depends(get_session)):
    try:
        created = AppointmentsService.create_appointment(db=db, payload=payload)
    except ValueError as exc:
        detail = str(exc)
        if detail == "Conflito de horário":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    return SchedulingResponse.from_entity(created)


@router.put("/{scheduling_id}", response_model=SchedulingResponse, dependencies=[Depends(require_roles(UserRole.CLIENT, UserRole.EMPLOYEE))])
def update_appointment(scheduling_id: UUID, payload: UpdateSchedulingRequest, db: Session = Depends(get_session)):
    try:
        saved = AppointmentsService.update_appointment(db=db, scheduling_id=scheduling_id, payload=payload)
    except ValueError as exc:
        detail = str(exc)
        if detail == "Conflito de horário":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
        if detail == "Appointment date is required":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    return SchedulingResponse.from_entity(saved)


@router.delete("/{scheduling_id}", response_model=DeleteResponse, dependencies=[Depends(require_roles(UserRole.CLIENT, UserRole.EMPLOYEE))])
def delete_appointment(scheduling_id: UUID, db: Session = Depends(get_session)):
    try:
        saved = AppointmentsService.delete_appointment(db=db, scheduling_id=scheduling_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return DeleteResponse(
        success=True,
        message="Agendamento cancelado com sucesso",
        deleted_id=str(saved.id),
    )