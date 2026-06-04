from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from config.db import get_session
from infra.repository import UserRepository, ClientRepository, EstablishmentRepository, PlanRepository
from middleware.auth import AuthError, create_access_token
from schema import ErrorResponse, TokenResponse, RegisterRequest, RegisterResponse
from utils.value_object import PasswordHasher
from utils.enum import UserRole
from domain.entities import User, Client, Establishment
from domain.service import StripeService

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


@router.post(
	"/register",
	response_model=RegisterResponse,
	status_code=status.HTTP_201_CREATED,
	responses={
		400: {"model": ErrorResponse},
		500: {"model": ErrorResponse},
	},
)
def register(payload: RegisterRequest, db: Session = Depends(get_session)) -> RegisterResponse:
	plan_repo = PlanRepository(db)
	plan_page = plan_repo.list_by_type(payload.plan, limit=1)
	plan = plan_page.data[0] if plan_page.data else None
	if plan is None:
		raise AuthError(status_code=400, error="plan_not_found", detail="Plano nao encontrado")

	stripe_service = StripeService()
	stripe_customer_id = stripe_service.create_customer(
		email=payload.user.email,
		name=payload.user.user_name,
	)

	user = User(
		id=None,
		user_name=payload.user.user_name,
		email=payload.user.email,
		phone_number=str(payload.user.phone_number),
		password_hash=PasswordHasher.to_hash(payload.user.password),
		role=UserRole.CLIENT,
		active_status=False,
		img_url="standart_img.png",
		created_at=None,
		updated_at=None,
	)
	user_repo = UserRepository(db)
	saved_user = user_repo.create(user)

	client = Client(
		id=None,
		user=saved_user,
		plan=plan,
		stripe_customer_id=stripe_customer_id,
	)
	client_repo = ClientRepository(db)
	saved_client = client_repo.create(client)

	due_date = datetime.now(timezone.utc) + timedelta(days=14)
	img_url = payload.establishment.img_url or "standart_img.png"
	chatbot_phone = (
		str(payload.establishment.chatbot_phone_number)
		if payload.establishment.chatbot_phone_number
		else None
	)

	establishment = Establishment(
		id=None,
		client=saved_client,
		stripe_subscription_id=None,
		waba_id="",
		whatsapp_business_token="",
		google_calendar_access_token=None,
		google_calendar_refresh_token=None,
		google_calendar_expiry=None,
		google_calendar_id=None,
		establishment_name=payload.establishment.establishment_name,
		cnpj=payload.establishment.cnpj,
		chatbot_phone_number=chatbot_phone,
		address=payload.establishment.address,
		img_url=img_url,
		subscription_date=datetime.now(timezone.utc),
		due_date=due_date,
		trial_active=True,
		available_hours=payload.establishment.available_hours,
	)

	establishment_repo = EstablishmentRepository(db)
	saved_establishment = establishment_repo.create(establishment)

	metadata = {
		"client_id": saved_client.id,
		"user_id": saved_user.id,
		"establishment_id": saved_establishment.id,
		"plan_id": plan.id,
		"billing_cycle": payload.billing_cycle,
		"employee_count": payload.employee_count,
	}

	try:
		checkout = stripe_service.create_checkout_session(
			customer_id=stripe_customer_id,
			plan=plan,
			employee_count=payload.employee_count,
			billing_cycle=payload.billing_cycle,
			metadata=metadata,
		)
	except ValueError as exc:
		raise AuthError(status_code=400, error="stripe_error", detail=str(exc)) from exc
	except Exception as exc:
		raise AuthError(status_code=500, error="stripe_error", detail="Falha ao criar checkout") from exc

	return RegisterResponse(checkout_url=checkout.url, session_id=checkout.session_id)
