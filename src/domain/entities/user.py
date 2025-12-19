from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from utils.enum import UserRole


@dataclass
class User:
    
    id: str | None # Lembrar de usar o UUID ao invés de id númerico
    user_name: str
    email: str
    phone_number: str
    role: UserRole
    active_status: bool | None
    img_url: str | None
    created_at: datetime | None
    updated_at: datetime | None
    
    def __post_init__(self):
        if not self.user_name or not isinstance(self.user_name, str):
            raise ValueError("User name is incorrect, must to be String")
        if not self.email or len(self.email) < 10:
            raise ValueError("Email is incorrect, is too short")
        if not self.email or '@' not in self.email:
            raise ValueError("Email is incorrect, must be have '@'")
        if not self.phone_number or len(self.phone_number) < 8:
            raise ValueError("Phone number is incorrect, is too short")
        if not isinstance(self.role, UserRole):
            raise ValueError("User Role is incorrect, must be a ADMIN, CLIENT or EMPLOYEE")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "role": self.role.value,
            "active_status": self.active_status,
            "img_url": self.img_url,
            "created_at": self.created_at.isoformat(sep=" ") if self.created_at else None,
            "updated_at": self.updated_at.isoformat(sep=" ") if self.updated_at else None,
        }
    
    @staticmethod
    def from_dict(data: dict) -> User:
        role_data = data.get("role")
        if isinstance(role_data, str):
            role = UserRole(role_data)
        elif isinstance(role_data, UserRole):
            role = role_data
        else:
            role = role_data
        
        return User(
            id=data.get("id"),
            user_name=data.get("user_name"),
            email=data.get("email"),
            phone_number=data.get("phone_number"),
            role=role,
            active_status=data.get("active_status"),
            img_url=data.get("img_url"),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data.get("updated_at")) if data.get("updated_at") else None,
        )
