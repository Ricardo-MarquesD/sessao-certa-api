Para executar o projeto:
poetry run python -m uvicorn main:app --reload --port 8000 --app-dir src

Workers
poetry run python scripts/worker_runner.py

ngrok:
ngrok http 8000

testes:
poetry run pytest -v

Google Calendar:
- Conectar: `GET /google-calendar/connect/{establishment_id}`
- Callback OAuth: `GET /google-calendar/callback?code=...&state=...`
- Desconectar: `DELETE /google-calendar/disconnect/{establishment_id}`

WhatsApp:
- Registrar: `POST /whatsapp/register`
- Webhook: `POST /whatsapp/webhook`
- Desconectar: `DELETE /whatsapp/disconnect/{establishment_id}`

Agendamentos manuais:
- Listar: `GET /appointments?establishment_id=...`
- Criar: `POST /appointments`
- Detalhar: `GET /appointments/{scheduling_id}`
- Atualizar: `PUT /appointments/{scheduling_id}`
- Cancelar: `DELETE /appointments/{scheduling_id}`

Imagens:
- Upload: `POST /images` (multipart/form-data, campo `file`)
- Remover: `DELETE /images?img_url=...`
- Atualizar imagem do usuario: `PUT /users/{user_id}/image`
- Atualizar imagem do estabelecimento: `PUT /establishments/{establishment_id}/image`
