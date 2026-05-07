from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.db import get_session
from infra.repository import EstablishmentRepository
from schema import EstablishmentResponse, UpdateEstablishmentImgRequest


router = APIRouter(prefix="/establishments")


@router.put("/{establishment_id}/image", response_model=EstablishmentResponse, status_code=status.HTTP_200_OK)
def update_establishment_image(
    establishment_id: UUID,
    payload: UpdateEstablishmentImgRequest,
    db: Session = Depends(get_session),
):
    repo = EstablishmentRepository(db)
    establishment = repo.get_by_id(establishment_id)

    if establishment is None:
        raise HTTPException(status_code=404, detail="Establishment not found")

    establishment.img_url = payload.img_url
    saved = repo.update(establishment)
    return EstablishmentResponse.from_entity(saved)
