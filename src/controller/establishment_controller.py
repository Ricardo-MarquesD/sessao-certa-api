from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import get_session
from infra.repository import ClientRepository, EstablishmentRepository
from utils.enum import UserRole
from middleware.auth import get_current_user, require_roles
from schema import EstablishmentResponse, UpdateEstablishmentImgRequest, UpdateEstablishmentRequest

router = APIRouter(prefix="/establishments", tags=["Establishments"])


def _get_client_establishment(db: Session, current_user):
    client_repo = ClientRepository(db)
    client = client_repo.get_by_user_id(current_user.id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    establishment_repo = EstablishmentRepository(db)
    establishment = establishment_repo.get_by_client_id(client.id)
    if establishment is None:
        raise HTTPException(status_code=404, detail="Establishment not found")

    return establishment


@router.get("", response_model=EstablishmentResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def get_establishment(
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    establishment = _get_client_establishment(db, current_user)
    return EstablishmentResponse.from_entity(establishment)


@router.put("", response_model=EstablishmentResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def update_establishment(
    payload: UpdateEstablishmentRequest,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if payload.due_date is not None or payload.trial_active is not None:
        raise HTTPException(status_code=403, detail="Sem permissao para alterar dados de assinatura")

    repo = EstablishmentRepository(db)
    establishment = _get_client_establishment(db, current_user)

    if payload.establishment_name is not None:
        establishment.establishment_name = payload.establishment_name
    if payload.chatbot_phone_number is not None:
        establishment.chatbot_phone_number = payload.chatbot_phone_number
    if payload.address is not None:
        establishment.address = payload.address
    if payload.available_hours is not None:
        establishment.available_hours = payload.available_hours

    saved = repo.update(establishment)
    return EstablishmentResponse.from_entity(saved)

@router.put("/{establishment_id}/image", response_model=EstablishmentResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def update_establishment_image(
    establishment_id: UUID,
    payload: UpdateEstablishmentImgRequest,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    repo = EstablishmentRepository(db)
    establishment = repo.get_by_id(establishment_id)

    if establishment is None:
        raise HTTPException(status_code=404, detail="Establishment not found")

    if str(establishment.client.user.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Sem permissao para alterar este estabelecimento")

    establishment.img_url = payload.img_url
    saved = repo.update(establishment)
    return EstablishmentResponse.from_entity(saved)
