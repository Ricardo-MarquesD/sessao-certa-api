from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session

from config.db import get_session
from config.settings import settings
from domain.entities import User
from infra.repository import UserRepository
from utils.enum import UserRole


@dataclass
class AuthError(Exception):
	status_code: int
	error: str
	detail: str | None = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def _ensure_jwt_config() -> tuple[str, str]:
	secret = settings.token_jwt_secret_key
	algorithm = settings.signature_algorithm or "HS256"
	if not secret:
		raise AuthError(status_code=500, error="jwt_config_error", detail="JWT secret nao configurado")
	return secret, algorithm


def create_access_token(*, user_id: UUID | str, email: str, role: UserRole | str, expires_minutes: int | None = None) -> str:
	secret, algorithm = _ensure_jwt_config()
	expires_minutes = expires_minutes or settings.access_token_expire_minutes
	now = datetime.now(timezone.utc)
	expire = now + timedelta(minutes=int(expires_minutes))
	payload = {
		"sub": str(user_id),
		"email": email,
		"role": role.value if isinstance(role, UserRole) else str(role),
		"iat": now,
		"exp": expire,
	}
	return jwt.encode(payload, secret, algorithm=algorithm)


def get_current_user(
	token: str | None = Depends(oauth2_scheme),
	db: Session = Depends(get_session),
) -> User:
	if not token:
		raise AuthError(status_code=401, error="not_authenticated", detail="Token ausente")
	secret, algorithm = _ensure_jwt_config()
	try:
		payload = jwt.decode(token, secret, algorithms=[algorithm])
	except ExpiredSignatureError as exc:
		raise AuthError(status_code=401, error="token_expired", detail="Token expirado") from exc
	except JWTError as exc:
		raise AuthError(status_code=401, error="invalid_token", detail="Token invalido") from exc

	subject = payload.get("sub")
	if not subject:
		raise AuthError(status_code=401, error="invalid_token", detail="Token sem subject")

	try:
		user_id = UUID(str(subject))
	except ValueError as exc:
		raise AuthError(status_code=401, error="invalid_token", detail="Subject do token invalido") from exc

	repo = UserRepository(db)
	user = repo.get_by_id(user_id)
	if user is None:
		raise AuthError(status_code=401, error="user_not_found", detail="Usuario nao encontrado")
	if not user.is_active():
		raise AuthError(status_code=403, error="inactive_user", detail="Usuario inativo")

	return user


def require_roles(*allowed_roles: UserRole | str):
	allowed = {
		role.value if isinstance(role, UserRole) else str(role)
		for role in allowed_roles
	}

	def dependency(current_user: User = Depends(get_current_user)) -> User:
		if allowed and current_user.role.value not in allowed:
			raise AuthError(status_code=403, error="forbidden", detail="Sem permissao para acessar este recurso")
		return current_user

	return dependency
