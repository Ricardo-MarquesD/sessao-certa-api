from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
from ...config import Base
from enum import Enum as enum

class UserRole(enum):
    CLIENT = 0
    EMPLOYEE = 1
    ADMIN = 2

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    user_name = Column(String(150), nullable = False)
    password_hash = Column(String(255), nullable = False)
    phone_number = Column(String(30), nullable = False)
    email = Column(String(320), nullable = False)
    role = Column(Enum(UserRole), nullable = False)
    active_status = Column(Boolean, nullable = False)
    create_in = Column(DateTime, nullable = False, server_default = func.current_timestamp())
    update_in = Column(DateTime, nullable = False, server_default = func.current_timestamp(), onupdate = func.current_timestamp())

    __mapper_args__ = {
        "polymorphic_identity": "user", '''<--- Adicionar um na client e em employee'''
        "polymorphic_on": role
    }

    def __repr__(self):
        create_str = self.create_in.strftime("%Y-%m-%d %H:%M:%S") if self.create_in else None
        update_str = self.update_in.strftime("%Y-%m-%d %H:%M:%S") if self.update_in else None
        return (
            f"<User(id={self.id}, name='{self.user_name}', email='{self.email}', "
            f"role='{self.role.name}', active_status={self.active_status}, "
            f"create_in={create_str}, update_in={update_str})>"
        )
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone_number": self.phone_number,
            "email": self.email,
            "role": self.role.name,
            "active_status": self.active_status,
            "create_in": self.create_in.strftime("%Y-%m-%d %H:%M:%S") if self.create_in else None,
            "update_in": self.update_in.strftime("%Y-%m-%d %H:%M:%S") if self.update_in else None
        }