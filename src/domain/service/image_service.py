from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import UploadFile


class ImageService:
    _ALLOWED_CONTENT_TYPES = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    }
    _EXT_BY_CONTENT_TYPE = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    _MAX_BYTES = 5 * 1024 * 1024

    @staticmethod
    def _img_root() -> Path:
        return Path(__file__).resolve().parents[2] / "img"

    @staticmethod
    def build_public_url(filename: str, *, base_url: str) -> str:
        base = base_url.rstrip("/")
        return f"{base}/img/{filename}"

    @staticmethod
    def save_upload(file: UploadFile, *, base_url: str) -> dict:
        if not file.content_type:
            raise ValueError("Tipo de imagem nao informado")
        if file.content_type not in ImageService._ALLOWED_CONTENT_TYPES:
            raise ValueError("Tipo de imagem nao suportado")

        ext = ImageService._EXT_BY_CONTENT_TYPE[file.content_type]
        filename = f"{uuid4().hex}{ext}"

        root = ImageService._img_root()
        root.mkdir(parents=True, exist_ok=True)

        size = 0
        target_path = root / filename
        with target_path.open("wb") as target:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > ImageService._MAX_BYTES:
                    target_path.unlink(missing_ok=True)
                    raise ValueError("Imagem maior que 5 MB")
                target.write(chunk)

        img_url = ImageService.build_public_url(filename, base_url=base_url)
        return {
            "img_url": img_url,
            "filename": filename,
            "size": size,
            "content_type": file.content_type,
        }

    @staticmethod
    def delete_by_url(img_url: str) -> dict:
        parsed = urlparse(img_url)
        path = parsed.path if parsed.scheme or parsed.netloc else img_url
        if not path.startswith("/img/"):
            raise ValueError("Caminho invalido")

        rel = path.replace("/img/", "", 1).lstrip("/")
        root = ImageService._img_root()
        target = (root / rel).resolve()
        root_resolved = root.resolve()

        if not target.is_relative_to(root_resolved):
            raise ValueError("Caminho invalido")

        target.unlink(missing_ok=True)
        return {
            "message": "Imagem removida",
            "deleted_path": str(target),
        }
