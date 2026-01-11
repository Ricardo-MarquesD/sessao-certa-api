from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Any | None = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)

class MessageResponse(BaseModel):
    message: str

class DeleteResponse(BaseModel):
    success: bool = True
    message: str = "Registro deletado com sucesso"
    deleted_id: str | int | None = None

class PaginatedResponse(BaseModel):
    data: list[Any]
    cursor: str | None = None
    has_more: bool = False
    total_count: int | None = None
