from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from config.db import get_session
from infra.repository import ClientRepository, CustomerRepository, EstablishmentRepository
from middleware.auth import get_current_user, require_roles
from schema import CustomerDetailResponse, CustomerResponse, PaginatedResponse
from utils.enum import UserRole

router = APIRouter(prefix="/customers", tags=["Customers"])


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


@router.get("", response_model=PaginatedResponse, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def list_customers(
    search: str | None = Query(default=None, min_length=1),
    phone_number: str | None = Query(default=None, min_length=8),
    cursor: str | None = None,
    limit: int = Query(default=15, ge=1, le=100),
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    establishment = _get_client_establishment(db, current_user)
    repo = CustomerRepository(db)

    if phone_number:
        customer = repo.get_by_phone_number(phone_number, establishment.id)
        data = [CustomerResponse.from_entity(customer)] if customer else []
        return PaginatedResponse(
            data=data,
            cursor=None,
            has_more=False,
            total_count=1 if customer else 0,
        )

    if search:
        paginated = repo.search_by_name(search, establishment.id, cursor=cursor, limit=limit)
    else:
        paginated = repo.list_by_establishment_id(establishment.id, cursor=cursor, limit=limit)

    return PaginatedResponse(
        data=[CustomerResponse.from_entity(customer) for customer in paginated.data],
        cursor=paginated.cursor,
        has_more=paginated.has_more,
        total_count=paginated.total_count,
    )


@router.get("/{customer_id}", response_model=CustomerDetailResponse, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    repo = CustomerRepository(db)
    customer = repo.get_by_id(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    establishment = _get_client_establishment(db, current_user)
    if str(customer.establishment.id) != str(establishment.id):
        raise HTTPException(status_code=403, detail="Sem permissao para acessar este cliente")

    return CustomerDetailResponse.from_entity(customer)
