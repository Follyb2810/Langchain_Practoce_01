# 🔹 1. Middleware in FastAPI

Middleware is code that runs **before and/or after every request**.
Think of it as a **pipeline** through which every request/response flows.

### Basic Middleware Example

```python
from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)  # call the actual route
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

**Explanation:**

1. `request` → incoming HTTP request
2. `call_next` → the function that executes the actual route
3. You can manipulate **request** before calling the route
4. You can manipulate **response** after the route finishes

Middleware is perfect for:

* Logging requests/responses
* Global authentication checks
* Setting headers or CORS policies

---

# 🔹 2. Authentication (AuthN)

Authentication = verifying **who the user is**.

In FastAPI, the most common pattern is **OAuth2 + JWT**.

### Minimal JWT Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Usage in routes:**

```python
@app.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return current_user
```

* `OAuth2PasswordBearer` extracts the token from the **Authorization header**
* `Depends(get_current_user)` injects the authenticated user into the route

---

# 🔹 3. Authorization (AuthZ)

Authorization = verifying **what the user can do**.

You can do this **on top of authentication**:

```python
def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@app.get("/admin")
def read_admin(current_user: dict = Depends(require_admin)):
    return {"message": "Welcome admin!"}
```

* AuthZ is usually **role-based** or **permission-based**
* Can combine **multiple dependencies**: `Depends(get_current_user)` → `Depends(require_admin)`

---

# 🔹 4. Combining Middleware + Auth

You **can put authentication in middleware**, but it’s often **better as a dependency**, because:

* Middleware runs for **every request**, including static files or docs
* Dependency injection allows **route-specific auth** and **access to query/path parameters**

**Middleware example for logging auth info:**

```python
@app.middleware("http")
async def log_user(request: Request, call_next):
    token = request.headers.get("Authorization")
    print(f"Token: {token}")  # log for debugging
    response = await call_next(request)
    return response
```

---

# 🔹 5. FastAPI Security Utilities

FastAPI provides built-in classes for **auth/permissions**:

| Class                       | Use Case                       |
| --------------------------- | ------------------------------ |
| `OAuth2PasswordBearer`      | Bearer token extraction        |
| `OAuth2PasswordRequestForm` | Form data for login            |
| `APIKeyHeader`              | API key in headers             |
| `HTTPBasic`                 | Basic auth for simple services |

You can combine **Depends + security classes** to build robust auth systems.

---

# 🔹 6. Summary

* **Middleware** = global pre/post processing of requests
* **Authentication** = verify user identity (JWT, OAuth2, API keys)
* **Authorization** = verify user permissions (role-based, ownership checks)
* Best practice in FastAPI:

  * Use **Depends** for auth logic per route
  * Use middleware for **logging, headers, CORS, metrics**



Perfect! Let’s build a **complete FastAPI flow** where you:

1. Verify a JWT auth token
2. Extract the `user_id` from it
3. Inject it into downstream routes using **dependencies**

This is the **standard way FastAPI handles auth**.

---

## 🔹 1. Install required package

```bash
pip install fastapi "python-jose[cryptography]" uvicorn
```

* `python-jose` → JWT encode/decode

---

## 🔹 2. JWT Utility

```python
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(user_id: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
```

---

## 🔹 3. Dependency to verify token

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # token endpoint

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Verify token and return user_id
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

* `Depends(oauth2_scheme)` → extracts the token from `Authorization: Bearer <token>`
* Returns **user\_id**, which is ready to inject into routes

---

## 🔹 4. Token generation route (for testing)

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/token")
def login():
    # For demo, we hardcode a user_id
    user_id = "123"
    token = create_access_token(user_id)
    return {"access_token": token, "token_type": "bearer"}
```

---

## 🔹 5. Protected Route (user\_id injected)

```python
@app.get("/me")
def read_me(user_id: str = Depends(get_current_user_id)):
    return {"user_id": user_id, "message": "Hello authenticated user!"}
```

**Flow:**

1. Client calls `/token` → gets JWT token
2. Client calls `/me` with header:

```
Authorization: Bearer <token>
```

3. FastAPI runs `get_current_user_id(token)` → extracts `user_id`
4. Route gets `user_id` automatically

Response example:

```json
{
  "user_id": "123",
  "message": "Hello authenticated user!"
}
```

---

## 🔹 6. Notes / Best Practices

* Use **`Depends(get_current_user_id)`** in any route that needs authentication
* You can create another dependency for **roles/authorization**:

```python
def require_admin(user_id: str = Depends(get_current_user_id)):
    user = get_user_from_db(user_id)
    if user.role != "admin":
        raise HTTPException(403, "Not authorized")
    return user
```

* This pattern lets you **chain dependencies**, making auth and authorization clean and reusable

---

If you want, I can extend this to a **full repo/service/controller structure** where every route automatically injects `user_id` and enforces auth, like a real production app.

Do you want me to do that next?
