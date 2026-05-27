from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from config.db import get_session
from domain.entities import Employee, User
from infra.repository import (
    ClientRepository,
    EmployeeRepository,
    EstablishmentRepository,
    UserRepository,
)
from middleware.auth import get_current_user, require_roles
from schema import (
    CreateEmployeeUserRequest,
    DeleteResponse,
    EmployeeDetailResponse,
    EmployeeResponse,
    PaginatedResponse,
    UpdateEmployeeRequest,
)
from utils.enum import UserRole
from utils.value_object import PasswordHasher

router = APIRouter(prefix="/employees", tags=["Employees"])


def _get_client_establishment(db: Session, current_user):
    client_repo = ClientRepository(db)
    client = client_repo.get_by_user_id(current_user.id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    establishment_repo = EstablishmentRepository(db)
    establishment = establishment_repo.get_by_client_id(client.id)
    if establishment is None:
        raise HTTPException(status_code=404, detail="Establishment not found")

    return client, establishment


def _ensure_employee_access(db: Session, employee_id: int, current_user):
    employee_repo = EmployeeRepository(db)

    if current_user.role == UserRole.EMPLOYEE:
        employee = employee_repo.get_by_user_id(current_user.id)
        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")
        if employee.id != employee_id:
            raise HTTPException(status_code=403, detail="Sem permissao para acessar este funcionario")
        return employee

    client, establishment = _get_client_establishment(db, current_user)
    employee = employee_repo.get_by_id(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    if str(employee.establishment.id) != str(establishment.id):
        raise HTTPException(status_code=403, detail="Sem permissao para acessar este funcionario")
    return employee


@router.get("", response_model=PaginatedResponse, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def list_employees(
    cursor: str | None = None,
    limit: int = Query(default=15, ge=1, le=100),
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    client, establishment = _get_client_establishment(db, current_user)
    repo = EmployeeRepository(db)
    paginated = repo.list_by_establishment_id(establishment.id, cursor=cursor, limit=limit)
    return PaginatedResponse(
        data=[EmployeeResponse.from_entity(employee) for employee in paginated.data],
        cursor=paginated.cursor,
        has_more=paginated.has_more,
        total_count=paginated.total_count,
    )


@router.get("/{employee_id}", response_model=EmployeeDetailResponse, dependencies=[Depends(require_roles(UserRole.CLIENT, UserRole.EMPLOYEE))])
def get_employee(
    employee_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    employee = _ensure_employee_access(db, employee_id, current_user)
    return EmployeeDetailResponse.from_entity(employee)


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def create_employee(
    payload: CreateEmployeeUserRequest,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    client, establishment = _get_client_establishment(db, current_user)
    employee_repo = EmployeeRepository(db)

    employee_count = employee_repo.count_by_establishment_id(establishment.id)
    if client.plan.max_employee is not None and employee_count >= client.plan.max_employee:
        raise HTTPException(status_code=403, detail="Limite de funcionarios atingido")

    user = User(
        id=None,
        user_name=payload.user_name,
        email=payload.email,
        phone_number=str(payload.phone_number),
        password_hash=PasswordHasher.to_hash(payload.password),
        role=UserRole.EMPLOYEE,
        active_status=True,
        img_url="standart_img.png",
        created_at=None,
        updated_at=None,
    )
    user_repo = UserRepository(db)
    saved_user = user_repo.create(user)

    employee = Employee(
        id=None,
        user=saved_user,
        establishment=establishment,
        percentage_commission=payload.percentage_commission,
        available_hours=payload.available_hours,
    )
    saved_employee = employee_repo.create(employee)
    return EmployeeResponse.from_entity(saved_employee)


@router.put("/{employee_id}", response_model=EmployeeResponse, dependencies=[Depends(require_roles(UserRole.CLIENT, UserRole.EMPLOYEE))])
def update_employee(
    employee_id: int,
    payload: UpdateEmployeeRequest,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    employee = _ensure_employee_access(db, employee_id, current_user)

    if payload.percentage_commission is not None:
        employee.percentage_commission = payload.percentage_commission
    if payload.available_hours is not None:
        employee.available_hours = payload.available_hours

    repo = EmployeeRepository(db)
    saved = repo.update(employee)
    return EmployeeResponse.from_entity(saved)


@router.delete("/{employee_id}", response_model=DeleteResponse, dependencies=[Depends(require_roles(UserRole.CLIENT))])
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    client, establishment = _get_client_establishment(db, current_user)
    repo = EmployeeRepository(db)
    employee = repo.get_by_id(employee_id)

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    if str(employee.establishment.id) != str(establishment.id):
        raise HTTPException(status_code=403, detail="Sem permissao para acessar este funcionario")

    deleted = repo.delete(employee_id)
    if not deleted:
        raise HTTPException(status_code=400, detail="Employee not deleted")

    user_repo = UserRepository(db)
    employee.user.active_status = False
    user_repo.update(employee.user)

    return DeleteResponse(
        success=True,
        message="Funcionario removido com sucesso",
        deleted_id=employee_id,
    )
