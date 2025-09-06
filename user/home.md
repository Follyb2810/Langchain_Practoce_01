# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from models import User
from schemas import UserCreate, UserRead, Token
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme, require_role
from crud import create_user
from datetime import timedelta

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register
@app.post("/auth/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.username == user_in.username) | (User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    user = create_user(db, user_in.username, user_in.email, user_in.password, user_in.role)
    return UserRead.model_validate(user)

# Token endpoint (OAuth2PasswordRequestForm expects form data)
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/auth/token", response_model=Token)
def login_for_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route: any authenticated
@app.get("/me", response_model=UserRead)
def read_me(current_user = Depends(require_role("user", "admin", "manager"))):
    # require_role returns current_user if role ok
    return UserRead.model_validate(current_user)

# Protected route: admin only
@app.get("/admin-only")
def admin_only(current_user = Depends(require_role("admin"))):
    return {"msg": f"Hello admin {current_user.username}"}
