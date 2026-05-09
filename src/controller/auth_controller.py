from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from config.db import get_session
from infra.repository import UserRepository
from middleware.auth import AuthError, create_access_token
from schema import ErrorResponse, TokenResponse
from utils.value_object import PasswordHasher

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post( "/login", response_model=TokenResponse, status_code=status.HTTP_200_OK, responses={
	401: {"model": ErrorResponse},
	403: {"model": ErrorResponse},
	500: {"model": ErrorResponse},}
	,)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)) -> TokenResponse:
	repo = UserRepository(db)
	user = repo.get_by_email(form_data.username)

	if user is None:
		raise AuthError(status_code=401, error="invalid_credentials", detail="Email ou senha invalidos")
	if not PasswordHasher.verify_password(form_data.password, user.password_hash):
		raise AuthError(status_code=401, error="invalid_credentials", detail="Email ou senha invalidos")
	if not user.is_active():
		raise AuthError(status_code=403, error="inactive_user", detail="Usuario inativo")

	token = create_access_token(user_id=user.id, email=user.email, role=user.role)
	return TokenResponse(access_token=token, token_type="bearer", role=user.role)
