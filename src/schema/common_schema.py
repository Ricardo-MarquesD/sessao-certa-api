from pydantic import BaseModel, Field
from datetime import datetime

class SuccessResponse(BaseModel):
    success: bool = True
    datail: str | None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
