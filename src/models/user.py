from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
from sqlalchemy.orm import relationship
from ...config import Base
from enum import Enum as enum

class UserRole(enum):
    CLIENT = 0
    EMPLOYEE = 1
    ADMIN = 2

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, nullable = False)
    name = Column(String(150), nullable = False)
    password = Column(String(255), nullable = False)
    phone_number = Column(String(30), nullable = False)
    email = Column(String(320), nullable = False)
    role = Column(Enum(UserRole), nullable = False)
    active_status = Column(Boolean, nullable = False)
    create_in = Column(DateTime, nullable = False, server_default = func.current_timestamp())
    update_in = Column(DateTime, nullable = False, server_default = func.current_timestamp(), onupdate = func.current_timestamp())
