from __future__ import annotations
from dataclasses import dataclass
from utils.value_object import TimeManipulation
from datetime import datetime, timedelta
from uuid import UUID
from .client import Client
from typing import Any

@dataclass
class Establishment():
    id: UUID | None 
    client: Client
    stripe_subscription_id: str | None
    waba_id: str
    whatsapp_business_token: str
    google_calendar_access_token: str | None
    google_calendar_refresh_token: str | None
    google_calendar_expiry: datetime | None
    google_calendar_id: str | None
    establishment_name: str
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
        
    def is_trial_active(self)->bool:
        return self.trial_active if self.trial_active is not None else False
    
    def is_subscription_valid(self)->bool:
        if self.due_date is None:
            return True
        res = TimeManipulation.time_diference(self.due_date)
        return res.total_seconds() > 0
    
    def time_until_due(self)->timedelta | None:
        if self.due_date is None:
            return None
        return TimeManipulation.time_diference(self.due_date)
        
    def to_dict(self)->dict[str, Any]:
        return {
            "id": self.id,
            "client": self.client.to_dict(),
            "stripe_subscription_id": self.stripe_subscription_id,
            "waba_id": self.waba_id,
            "whatsapp_business_token": self.whatsapp_business_token,
            "google_calendar_access_token": self.google_calendar_access_token,
            "google_calendar_refresh_token": self.google_calendar_refresh_token,
            "google_calendar_expiry": self.google_calendar_expiry.isoformat(sep=" ") if self.google_calendar_expiry else None,
            "google_calendar_id": self.google_calendar_id,
            "establishment_name": self.establishment_name,
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
            stripe_subscription_id = data.get("stripe_subscription_id"),
            waba_id = data.get("waba_id"),
            whatsapp_business_token = data.get("whatsapp_business_token"),
            google_calendar_access_token = data.get("google_calendar_access_token"),
            google_calendar_refresh_token = data.get("google_calendar_refresh_token"),
            google_calendar_expiry = datetime.fromisoformat(data.get("google_calendar_expiry")) if data.get("google_calendar_expiry") else None,
            google_calendar_id = data.get("google_calendar_id"),
            establishment_name = data.get("establishment_name"),
            cnpj = data.get("cnpj"),
            chatbot_phone_number = data.get("chatbot_phone_number"),
            address = data.get("address"),
            img_url = data.get("img_url"),
            subscription_date = datetime.fromisoformat(data.get("subscription_date")) if data.get("subscription_date") else None,
            due_date = datetime.fromisoformat(data.get("due_date")) if data.get("due_date") else None,
            trial_active = data.get("trial_active")
        )