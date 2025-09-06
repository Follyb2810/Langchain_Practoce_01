from typing import Optional
from sqlalchemy import Column, Integer, String, Float
from db import Base
from pydantic import BaseModel, EmailStr


class UserSchema(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # hashed_password = Column(String, nullable=False)
    # is_active = Column(Boolean, default=True)
    # role = Column(String, default="user")  # e.g., "user", "admin", "manager"


class UserModel(BaseModel):
    id: Optional[int] = None
    username: str
    email: str

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    role: str

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
