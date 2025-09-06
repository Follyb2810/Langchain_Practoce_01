# crud.py
from sqlalchemy.orm import Session
from models import User
from auth import hash_password

def create_user(db: Session, username: str, email: str, password: str, role: str = "user") -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
