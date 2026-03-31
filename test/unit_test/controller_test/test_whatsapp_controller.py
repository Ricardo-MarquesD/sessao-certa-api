import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from controller.whatsapp_controller import router
from config.db import get_session
import aiohttp

# App de teste isolado — não usa main.py para não depender do banco real
app = FastAPI()
app.include_router(router)
app.dependency_overrides[get_session] = lambda: MagicMock()

BASE_PAYLOAD = {
    "establishment_id": 1,
    "waba_id": "waba-test-001",
    "phone_number_id": "phone-test-001",
    "code": "auth-code-123",
}


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestWhatsappRegister:

    def test_missing_fields_returns_400(self, client):
        """Payload incompleto deve retornar 400."""
        resp = client.post("/whatsapp/register", json={"establishment_id": 1})
        assert resp.status_code == 400
        assert "incompletos" in resp.json()["detail"]

    def test_establishment_not_found_returns_404(self, client):
        """Establishment inexistente deve retornar 404."""
        with patch("controller.whatsapp_controller.EstablishmentRepository") as MockRepo:
            MockRepo.return_value.get_by_id.return_value = None
            resp = client.post("/whatsapp/register", json=BASE_PAYLOAD)

        assert resp.status_code == 404
        assert "Establishment" in resp.json()["detail"]

    def test_meta_http_error_returns_502(self, client):
        """Erro HTTP da API da Meta deve retornar 502."""
        error = aiohttp.ClientResponseError(
            request_info=MagicMock(), history=(), status=401
        )
        with (
            patch("controller.whatsapp_controller.EstablishmentRepository") as MockRepo,
            patch(
                "controller.whatsapp_controller.WhatsappService.get_permanent_token",
                new=AsyncMock(side_effect=error),
            ),
        ):
            MockRepo.return_value.get_by_id.return_value = MagicMock()
            resp = client.post("/whatsapp/register", json=BASE_PAYLOAD)

        assert resp.status_code == 502
        assert "Meta" in resp.json()["detail"]

    def test_meta_value_error_returns_502(self, client):
        """Erro de negócio retornado pela Meta (sem access_token) deve retornar 502."""
        with (
            patch("controller.whatsapp_controller.EstablishmentRepository") as MockRepo,
            patch(
                "controller.whatsapp_controller.WhatsappService.get_permanent_token",
                new=AsyncMock(side_effect=ValueError("Meta API did not return an access_token")),
            ),
        ):
            MockRepo.return_value.get_by_id.return_value = MagicMock()
            resp = client.post("/whatsapp/register", json=BASE_PAYLOAD)

        assert resp.status_code == 502
        assert "access_token" in resp.json()["detail"]

    def test_successful_registration(self, client):
        """Fluxo feliz: deve retornar 200 e gravar os dados no establishment."""
        mock_establishment = MagicMock()

        with (
            patch("controller.whatsapp_controller.EstablishmentRepository") as MockRepo,
            patch(
                "controller.whatsapp_controller.WhatsappService.get_permanent_token",
                new=AsyncMock(return_value="perm-token-xyz"),
            ),
            patch(
                "controller.whatsapp_controller.WhatsappService.subscribe_webhook",
                new=AsyncMock(),
            ),
        ):
            MockRepo.return_value.get_by_id.return_value = mock_establishment
            MockRepo.return_value.update.return_value = None
            resp = client.post("/whatsapp/register", json=BASE_PAYLOAD)

        assert resp.status_code == 200
        assert resp.json() == {"status": "connected"}

        # Garante que os campos foram atribuídos corretamente no establishment
        assert mock_establishment.waba_id == "waba-test-001"
        assert mock_establishment.chatbot_phone_number == "phone-test-001"
        assert mock_establishment.whatsapp_business_token == "perm-token-xyz"


class TestWhatsappDisconnect:

    def test_establishment_not_found_returns_404(self, client):
        with patch("controller.whatsapp_controller.EstablishmentRepository") as MockRepo:
            MockRepo.return_value.get_by_id.return_value = None
            resp = client.delete("/whatsapp/disconnect/1")

        assert resp.status_code == 404
        assert "Establishment" in resp.json()["detail"]

    def test_meta_http_error_returns_502(self, client):
        mock_establishment = MagicMock()
        mock_establishment.waba_id = "waba-test-001"
        mock_establishment.whatsapp_business_token = "token-xyz"

        error = aiohttp.ClientResponseError(
            request_info=MagicMock(), history=(), status=401
        )
        with (
            patch("controller.whatsapp_controller.EstablishmentRepository") as MockRepo,
            patch(
                "controller.whatsapp_controller.WhatsappService.unsubscribe_webhook",
                new=AsyncMock(side_effect=error),
            ),
        ):
            MockRepo.return_value.get_by_id.return_value = mock_establishment
            resp = client.delete("/whatsapp/disconnect/1")

        assert resp.status_code == 502
        assert "Meta" in resp.json()["detail"]

    def test_meta_value_error_returns_502(self, client):
        mock_establishment = MagicMock()
        mock_establishment.waba_id = "waba-test-001"
        mock_establishment.whatsapp_business_token = "token-xyz"

        with (
            patch("controller.whatsapp_controller.EstablishmentRepository") as MockRepo,
            patch(
                "controller.whatsapp_controller.WhatsappService.unsubscribe_webhook",
                new=AsyncMock(side_effect=ValueError("Meta API error: Invalid token")),
            ),
        ):
            MockRepo.return_value.get_by_id.return_value = mock_establishment
            resp = client.delete("/whatsapp/disconnect/1")

        assert resp.status_code == 502
        assert "Meta API error" in resp.json()["detail"]

    def test_successful_disconnect_with_credentials(self, client):
        mock_establishment = MagicMock()
        mock_establishment.waba_id = "waba-test-001"
        mock_establishment.chatbot_phone_number = "phone-test-001"
        mock_establishment.whatsapp_business_token = "token-xyz"

        with (
            patch("controller.whatsapp_controller.EstablishmentRepository") as MockRepo,
            patch(
                "controller.whatsapp_controller.WhatsappService.unsubscribe_webhook",
                new=AsyncMock(),
            ),
        ):
            MockRepo.return_value.get_by_id.return_value = mock_establishment
            MockRepo.return_value.update.return_value = None
            resp = client.delete("/whatsapp/disconnect/1")

        assert resp.status_code == 200
        assert resp.json() == {"status": "disconnected"}
        assert mock_establishment.waba_id is None
        assert mock_establishment.chatbot_phone_number is None
        assert mock_establishment.whatsapp_business_token is None

    def test_successful_disconnect_without_credentials(self, client):
        mock_establishment = MagicMock()
        mock_establishment.waba_id = None
        mock_establishment.chatbot_phone_number = None
        mock_establishment.whatsapp_business_token = None

        with patch("controller.whatsapp_controller.EstablishmentRepository") as MockRepo:
            MockRepo.return_value.get_by_id.return_value = mock_establishment
            MockRepo.return_value.update.return_value = None
            resp = client.delete("/whatsapp/disconnect/1")

        assert resp.status_code == 200
        assert resp.json() == {"status": "disconnected"}


class TestWhatsappWebhook:

    def test_webhook_returns_ok_and_enqueues_task_in_background(self, client, monkeypatch):
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {"phone_number_id": "phone-test-001"},
                                "messages": [
                                    {
                                        "from": "5511999999999",
                                        "id": "wamid-001",
                                        "text": {"body": "Oi"},
                                    }
                                ],
                            }
                        }
                    ]
                }
            ]
        }

        calls = []

        def fake_enqueue(webhook_payload):
            calls.append(webhook_payload)

        monkeypatch.setattr("controller.whatsapp_controller.WhatsappWebhookHelper.enqueue_process_message", fake_enqueue)

        resp = client.post("/whatsapp/webhook", json=payload)

        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
        assert calls == [payload]
