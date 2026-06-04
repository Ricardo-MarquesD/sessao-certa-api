Para executar o projeto:
poetry run python -m uvicorn main:app --reload --port 8000 --app-dir src

Workers
poetry run python scripts/worker_runner.py

ngrok:
ngrok http 8000

testes:
poetry run pytest -v

Autenticacao (JWT):
- Login: `POST /auth/login` (form-data: `username` = email, `password`)
- Retorno: `{ "access_token": "...", "token_type": "bearer", "role": "CLIENT|EMPLOYEE|ADMIN" }`
- Header para rotas protegidas: `Authorization: Bearer <token>`

Cadastro (Stripe Checkout):
- Register: `POST /auth/register`
- Payload:
	```json
	{
		"user": {
			"user_name": "Nome",
			"email": "email@exemplo.com",
			"phone_number": "+5511999999999",
			"password": "senha1234"
		},
		"establishment": {
			"establishment_name": "Meu Estabelecimento",
			"cnpj": "12345678000190",
			"chatbot_phone_number": "+5511999999999",
			"address": "Rua X, 123",
			"available_hours": null,
			"img_url": "standart_img.png"
		},
		"plan": "BRONZE",
		"employee_count": 3,
		"billing_cycle": "Mensalmente"
	}
	```
- Retorno: `{ "checkout_url": "...", "session_id": "..." }`
- Campos para teste:
	- `billing_cycle`: `Mensalmente` ou `Anualmente`
	- `employee_count`: inteiro >= 1
	- Preco mensal/anual usa os `price_id` configurados na Stripe (mensal e anual). Para anual, o cupom `cupom-anual` e aplicado.

RBAC:
- Roles: `CLIENT`, `EMPLOYEE`, `ADMIN`
- Ownership: para atualizar imagem de usuario, somente o proprio usuario ou `ADMIN`.

Google Calendar:
- Conectar: `GET /google-calendar/connect/{establishment_id}` (JWT + role CLIENT)
- Callback OAuth: `GET /google-calendar/callback?code=...&state=...`
- Desconectar: `DELETE /google-calendar/disconnect/{establishment_id}` (JWT + role CLIENT)

WhatsApp:
- Registrar: `POST /whatsapp/register` (JWT + role CLIENT)
- Webhook: `POST /whatsapp/webhook`
- Desconectar: `DELETE /whatsapp/disconnect/{establishment_id}` (JWT + role CLIENT)

Agendamentos manuais:
- Listar: `GET /appointments?establishment_id=...` (JWT + role CLIENT/EMPLOYEE)
- Criar: `POST /appointments` (JWT + role CLIENT/EMPLOYEE)
- Detalhar: `GET /appointments/{scheduling_id}` (JWT + role CLIENT/EMPLOYEE)
- Atualizar: `PUT /appointments/{scheduling_id}` (JWT + role CLIENT/EMPLOYEE)
- Cancelar: `DELETE /appointments/{scheduling_id}` (JWT + role CLIENT/EMPLOYEE)

Imagens:
- Upload: `POST /images` (JWT + role CLIENT/EMPLOYEE/ADMIN; multipart/form-data, campo `file`)
- Remover: `DELETE /images?img_url=...` (JWT + role ADMIN)
- Atualizar imagem do usuario: `PUT /users/{user_id}/image` (JWT + role CLIENT/EMPLOYEE/ADMIN + ownership)
- Atualizar imagem do estabelecimento: `PUT /establishments/{establishment_id}/image` (JWT + role CLIENT)
