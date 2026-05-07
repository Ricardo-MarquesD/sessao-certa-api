from fastapi import FastAPI
from fastapi.testclient import TestClient

from controller import image_controller as image_controller_module
from controller.image_controller import router


def build_client(monkeypatch):
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_upload_image_success(monkeypatch):
    def fake_save_upload(file, *, base_url):
        return {
            "img_url": f"{base_url.rstrip('/')}/img/test.png",
            "filename": "test.png",
            "size": 10,
            "content_type": "image/png",
        }

    monkeypatch.setattr(image_controller_module.ImageService, "save_upload", fake_save_upload)

    client = build_client(monkeypatch)
    response = client.post(
        "/images",
        files={"file": ("test.png", b"data", "image/png")},
    )

    assert response.status_code == 201
    assert response.json()["img_url"].endswith("/img/test.png")


def test_upload_image_returns_400_on_validation_error(monkeypatch):
    def fake_save_upload(file, *, base_url):
        raise ValueError("Tipo de imagem nao suportado")

    monkeypatch.setattr(image_controller_module.ImageService, "save_upload", fake_save_upload)

    client = build_client(monkeypatch)
    response = client.post(
        "/images",
        files={"file": ("test.txt", b"data", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Tipo de imagem nao suportado"


def test_delete_image_success(monkeypatch):
    def fake_delete_by_url(img_url):
        return {
            "message": "Imagem removida",
            "deleted_path": "/tmp/test.png",
        }

    monkeypatch.setattr(image_controller_module.ImageService, "delete_by_url", fake_delete_by_url)

    client = build_client(monkeypatch)
    response = client.delete("/images", params={"img_url": "https://example.com/img/test.png"})

    assert response.status_code == 200
    assert response.json()["message"] == "Imagem removida"


def test_delete_image_returns_400_on_validation_error(monkeypatch):
    def fake_delete_by_url(img_url):
        raise ValueError("Caminho invalido")

    monkeypatch.setattr(image_controller_module.ImageService, "delete_by_url", fake_delete_by_url)

    client = build_client(monkeypatch)
    response = client.delete("/images", params={"img_url": "invalid"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Caminho invalido"
