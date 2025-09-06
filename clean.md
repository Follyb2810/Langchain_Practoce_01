Perfect 🙌 You’re talking about **structuring a FastAPI app in a layered architecture** (clean separation: repository → service → controller → routes). This is how you make your app *scalable* and *maintainable*.

Let’s build it step by step.

---

## 🔹 Project Structure

Here’s a typical structure:

```
app/
│── main.py                # Entry point (FastAPI instance, include routers)
│── api/
│   ├── routes/            # Routers (endpoints)
│   │   └── user_routes.py
│   ├── controllers/       # Controllers (request → service)
│   │   └── user_controller.py
│   ├── services/          # Business logic
│   │   └── user_service.py
│   └── repositories/      # DB layer (SQLAlchemy / Prisma / etc.)
│       └── user_repository.py
│── models/
│   ├── user_model.py      # SQLAlchemy model
│── schemas/
│   ├── user_schema.py     # Pydantic models
│── core/
│   └── database.py        # DB session setup
```

---

## 🔹 Example: User Feature

### 1. Database Setup (`core/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/mydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### 2. SQLAlchemy Model (`models/user_model.py`)

```python
from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
```

---

### 3. Pydantic Schema (`schemas/user_schema.py`)

```python
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    full_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
```

---

### 4. Repository (`api/repositories/user_repository.py`)

Handles **DB access** only.

```python
from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas.user_schema import UserCreate

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(full_name=user.full_name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()
```

---

### 5. Service (`api/services/user_service.py`)

Contains **business logic**.

```python
from sqlalchemy.orm import Session
from app.api.repositories import user_repository
from app.schemas.user_schema import UserCreate

def register_user(db: Session, user: UserCreate):
    existing_user = user_repository.get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Email already registered")
    return user_repository.create_user(db, user)

def list_users(db: Session, skip: int = 0, limit: int = 10):
    return user_repository.get_users(db, skip, limit)
```

---

### 6. Controller (`api/controllers/user_controller.py`)

Maps **requests → services**.

```python
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate
from app.api.services import user_service

def create_user_controller(db: Session, user: UserCreate):
    return user_service.register_user(db, user)

def list_users_controller(db: Session, skip: int, limit: int):
    return user_service.list_users(db, skip, limit)
```

---

### 7. Routes (`api/routes/user_routes.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserResponse
from app.api.controllers import user_controller
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_controller.create_user_controller(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return user_controller.list_users_controller(db, skip, limit)
```

---

### 8. Main App (`main.py`)

```python
from fastapi import FastAPI
from app.api.routes import user_routes
from app.core.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="My FastAPI App")

app.include_router(user_routes.router)
```

---

✅ With this structure:

* **Repository** → DB only
* **Service** → business logic
* **Controller** → connects service ↔ route
* **Routes** → HTTP endpoints

This way your app is **clean, testable, and scalable**.

---

👉 Do you want me to extend this example to include **auth (JWT login/register)** so you see how repository/service/controller split works in a real-world flow?
