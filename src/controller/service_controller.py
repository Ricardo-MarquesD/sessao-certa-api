from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from config.db import get_session
from domain.entities import Service
from infra.repository import (
    ClientRepository,
    EmployeeRepository,
    EstablishmentRepository,
    ServiceRepository,
)
from middleware.auth import get_current_user, require_roles
from schema import (
    CreateServiceUserRequest,
    DeleteResponse,
    PaginatedResponse,
    ServiceResponse,
    UpdateServiceRequest,
)
from utils.enum import UserRole

router = APIRouter(prefix="/services", tags=["Services"])


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


def _ensure_establishment_access(db: Session, establishment_id: UUID, current_user):
    if current_user.role == UserRole.EMPLOYEE:
        employee_repo = EmployeeRepository(db)
        employee = employee_repo.get_by_user_id(current_user.id)
        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        if str(employee.establishment.id) != str(establishment_id):
            raise HTTPException(status_code=403, detail="Sem permissao para acessar este estabelecimento")
        return employee.establishment

    establishment = _get_client_establishment(db, current_user)
    if str(establishment.id) != str(establishment_id):
        raise HTTPException(status_code=403, detail="Sem permissao para acessar este estabelecimento")
    return establishment


@router.get("", response_model=PaginatedResponse, dependencies=[Depends(require_roles(UserRole.CLIENT, UserRole.EMPLOYEE))])
def list_services(
    establishment_id: UUID = Query(...),
    active: bool | None = Query(default=None),
    cursor: str | None = None,
    limit: int = Query(default=15, ge=1, le=100),
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    _ensure_establishment_access(db, establishment_id, current_user)
    repo = ServiceRepository(db)
    if active is None:
        paginated = repo.list_by_establishment_id(establishment_id, cursor=cursor, limit=limit)
    else:
        paginated = repo.list_active_by_establishment_id(active, establishment_id, cursor=cursor, limit=limit)
    return PaginatedResponse(
        data=[ServiceResponse.from_entity(service) for service in paginated.data],
        cursor=paginated.cursor,
        has_more=paginated.has_more,
        total_count=paginated.total_count,
    )


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def create_service(
    payload: CreateServiceUserRequest,
    establishment_id: UUID = Query(...),
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    establishment = _ensure_establishment_access(db, establishment_id, current_user)
    service = Service(
        id=uuid4(),
        establishment=establishment,
        service_name=payload.service_name,
        description_service=payload.description_service,
        time_duration=payload.time_duration,
        price=payload.price,
        active=payload.active,
    )
    repo = ServiceRepository(db)
    saved = repo.create(service)
    return ServiceResponse.from_entity(saved)


@router.put("/{service_id}", response_model=ServiceResponse, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def update_service(
    service_id: UUID,
    payload: UpdateServiceRequest,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    repo = ServiceRepository(db)
    service = repo.get_by_id(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    establishment = _get_client_establishment(db, current_user)
    if str(service.establishment.id) != str(establishment.id):
        raise HTTPException(status_code=403, detail="Sem permissao para acessar este servico")

    if payload.service_name is not None:
        service.service_name = payload.service_name
    if payload.description_service is not None:
        service.description_service = payload.description_service
    if payload.time_duration is not None:
        service.time_duration = payload.time_duration
    if payload.price is not None:
        service.price = payload.price

    saved = repo.update(service)
    return ServiceResponse.from_entity(saved)


@router.delete("/{service_id}", response_model=DeleteResponse, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def delete_service(
    service_id: UUID,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    repo = ServiceRepository(db)
    service = repo.get_by_id(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    establishment = _get_client_establishment(db, current_user)
    if str(service.establishment.id) != str(establishment.id):
        raise HTTPException(status_code=403, detail="Sem permissao para acessar este servico")

    deleted = repo.delete(service_id)
    if not deleted:
        raise HTTPException(status_code=400, detail="Service not deleted")

    return DeleteResponse(
        success=True,
        message="Servico removido com sucesso",
        deleted_id=str(service_id),
    )
