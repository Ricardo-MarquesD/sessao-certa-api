from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .establishment import Establishment

@dataclass
class MarketingMessage():
    id: int | None
    establishment: Establishment
    title: str | None
    content: str | None

    def __post_init__(self):
        if not isinstance(self.establishment, Establishment):
            raise ValueError("Establishment must be a Establishment instance")
        
    def to_dict(self)->dict[str,Any]:
        return {
            "id": self.id,
            "establishment": self.establishment.to_dict(),
            "title": self.title,
            "content": self.content
        }
    
    @staticmethod
    def from_dict(data:dict)->MarketingMessage:
        establishment_data = data.get("establishment")

        return MarketingMessage(
            id=data.get("id"),
            establishment=Establishment.from_dict(establishment_data) if isinstance(establishment_data, dict) else establishment_data,
            title=data.get("title"),
            content=data.get("content")
        )