from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
from sqlalchemy.dialects.mysql import CHAR
from enum import Enum as enum
from config import Base
import uuid

class UserRole(enum):
    CLIENT = "CLIENT"
    EMPLOYEE = "EMPLOYEE"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, autoincrement = True,nullable = False)
    uuid = Column(CHAR(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    user_name = Column(String(150), nullable = False)
    password_hash = Column(String(255), nullable = False)
    phone_number = Column(String(30), nullable = False)
    email = Column(String(320), nullable = False)
    role = Column(Enum(UserRole), nullable = False)
    active_status = Column(Boolean, nullable = False, server_default = "0")
    create_in = Column(DateTime, server_default = func.current_timestamp())
    update_in = Column(DateTime, server_default = func.current_timestamp(), onupdate = func.current_timestamp())

    def __repr__(self):
        create_str = self.create_in.strftime("%Y-%m-%d %H:%M:%S") if self.create_in else None
        update_str = self.update_in.strftime("%Y-%m-%d %H:%M:%S") if self.update_in else None
        return (
            f"<User(id={self.uuid}, name='{self.user_name}', email='{self.email}', "
            f"role='{self.role.value}', active_status={self.active_status}, "
            f"create_in={create_str}, update_in={update_str})>"
        )
    def to_dict(self):
        return {
            "id": self.uuid,
            "name": self.user_name,
            "phone_number": self.phone_number,
            "email": self.email,
            "role": self.role.value,
            "active_status": self.active_status,
            "create_in": self.create_in.strftime("%Y-%m-%d %H:%M:%S") if self.create_in else None,
            "update_in": self.update_in.strftime("%Y-%m-%d %H:%M:%S") if self.update_in else None
        }