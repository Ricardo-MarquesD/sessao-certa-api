from pydantic import BaseModel, Field, field_validator
from typing import Literal

class ImageUploadResponse(BaseModel):
    img_url: str = Field(description="URL para acessar a imagem")
    filename: str = Field(description="Nome do arquivo gerado")
    size: int = Field(description="Tamanho em bytes")
    content_type: str = Field(description="MIME type")

class ImageDeleteResponse(BaseModel):
    message: str
    deleted_path: str

class ImageValidationError(BaseModel):
    error: str
    detail: str
