from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Any


@dataclass
class Context:
    id: UUID | None
    establishments_id: int
    customers_id: int | None
    phone_number: str
    last_message_id: str | None
    context_arrow: str | None
    is_open: bool
    context_data: dict | None
    created_at: datetime | None
    updated_at: datetime | None
    expires_at: datetime

    def __post_init__(self):
        if len(self.phone_number) < 8:
            raise ValueError("Phone number is too short")
        if not isinstance(self.expires_at, datetime):
            raise ValueError("expires_at must be a datetime")

    def is_expired(self) -> bool:
        return datetime.now() >= self.expires_at

    def close(self) -> None:
        self.is_open = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "establishments_id": self.establishments_id,
            "customers_id": self.customers_id,
            "phone_number": self.phone_number,
            "last_message_id": self.last_message_id,
            "context_arrow": self.context_arrow,
            "is_open": self.is_open,
            "context_data": self.context_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat(),
        }

    @staticmethod
    def from_dict(data: dict) -> Context:
        return Context(
            id=data.get("id"),
            establishments_id=data.get("establishments_id"),
            customers_id=data.get("customers_id"),
            phone_number=data.get("phone_number"),
            last_message_id=data.get("last_message_id"),
            context_arrow=data.get("context_arrow"),
            is_open=data.get("is_open", False),
            context_data=data.get("context_data"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )
