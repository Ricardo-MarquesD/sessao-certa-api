from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from .client import Client
from typing import Any

@dataclass
class Establishment():
    id: str | None # Lembresse desse id ser o do UUID
    client: Client
    cnpj: str
    chatbot_phone_number: str | None
    address: str | None
    img_url: str | None
    subscription_date: datetime | None
    due_date: datetime | None
    trial_active: bool | None

    def __post_init__(self):
        if not isinstance(self.client, Client):
            raise ValueError("Client must be a Client instance")
        if not isinstance(self.cnpj, str) or len(self.cnpj) != 14:
            raise ValueError("CNPJ must be a string with 14 characters")
        
    def to_dict(self)->dict[str, Any]:
        return {
            "id": self.id,
            "client": self.client.to_dict(),
            "cnpj": self.cnpj,
            "chatbot_phone_number": self.chatbot_phone_number,
            "address": self.address,
            "img_url": self.img_url,
            "subscription_date": self.subscription_date.isoformat(sep=" ") if self.subscription_date else None,
            "due_date": self.due_date.isoformat(sep=" ") if self.due_date else None,
            "trial_active": self.trial_active
        }

    @staticmethod
    def from_dict(data: dict)->Establishment:
        client_data = data.get("client")
        
        return Establishment(
            id = data.get("id"),
            client = Client.from_dict(client_data) if isinstance(client_data, dict) else client_data,
            cnpj = data.get("cnpj"),
            chatbot_phone_number = data.get("chatbot_phone_number"),
            address = data.get("address"),
            img_url = data.get("img_url"),
            subscription_date = datetime.fromisoformat(data.get("subscription_date")) if data.get("subscription_date") else None,
            due_date = datetime.fromisoformat(data.get("due_date")) if data.get("due_date") else None,
            trial_active = data.get("trial_active")
        )