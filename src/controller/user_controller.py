from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from utils.enum import UserRole
from middleware.auth import get_current_user, require_roles
from config.db import get_session
from infra.repository import UserRepository
from schema import UpdateImgRequest, UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.put("/{user_id}/image", response_model=UserResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(require_roles(UserRole.CLIENT, UserRole.EMPLOYEE, UserRole.ADMIN))])
def update_user_image(
    user_id: UUID,
    payload: UpdateImgRequest,
    db: Session = Depends(get_session),
    current_user = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN and str(current_user.id) != str(user_id):
        raise HTTPException(status_code=403, detail="Sem permissao para alterar este usuario")
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.img_url = payload.img_url
    saved = repo.update(user)
    return UserResponse.from_entity(saved)
