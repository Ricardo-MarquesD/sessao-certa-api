from dataclasses import dataclass
from datetime import datetime
from utils.enum import UserRole


@dataclass
class User:
    
    id: str | None
    user_name: str
    email: str
    phone_number: str
    role: UserRole
    active_status: bool
    img_url: str | None
    created_at: datetime | None
    updated_at: datetime | None
    
    # def __post_init__(self):
        
    
    # def update_profile():
    
    def to_dict(self) -> dict:
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
    def from_dict(data: dict) -> "User":
        return User(
            id=data.get("id"),
            user_name=data["user_name"],
            email=data["email"],
            phone_number=data["phone_number"],
            role=UserRole(data["role"]) if isinstance(data["role"], str) else data["role"],
            active_status=data.get("active_status", False),
            img_url=data.get("img_url"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )
