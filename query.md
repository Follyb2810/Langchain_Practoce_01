### openssl rand -hex 32
### 1e043a07584c8827e181ebd0bf6db918a70dbc5cc580b868e9a57ed7935c3a88
## 🔹 Basic Example

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

👉 If you visit:

```
http://127.0.0.1:8000/items/?skip=5&limit=20
```

You’ll get:

```json
{"skip": 5, "limit": 20}
```

---

## 🔹 Optional Query Parameters

By default, if you give them default values, they become **optional**.

```python
@app.get("/users/")
def read_users(name: str | None = None):
    if name:
        return {"message": f"Hello {name}"}
    return {"message": "Hello Stranger"}
```

Example:

* `/users/?name=Eniola` → `{"message": "Hello Eniola"}`
* `/users/` → `{"message": "Hello Stranger"}`

---

## 🔹 Type Conversion

FastAPI automatically converts types:

```python
@app.get("/search/")
def search(q: str, page: int = 1, active: bool = True):
    return {"query": q, "page": page, "active": active}
```

URL:

```
/search/?q=doctor&page=2&active=false
```

Output:

```json
{"query": "doctor", "page": 2, "active": false}
```

---

## 🔹 Validation & Metadata with Query()

You can use `fastapi.Query` for extra validation:

```python
from fastapi import Query

@app.get("/products/")
def get_products(
    q: str = Query(..., min_length=3, max_length=50, description="Search term"),
    limit: int = Query(10, ge=1, le=100)
):
    return {"q": q, "limit": limit}
```

✅ Features here:

* `...` → required parameter
* `min_length`, `max_length` for string length
* `ge` (≥), `le` (≤) for numbers
* `description` shows up in Swagger docs

---

## 🔹 Multiple Values

Query params can accept multiple values:

```python
@app.get("/tags/")
def get_tags(tags: list[str] = Query([])):
    return {"tags": tags}
```

Request:

```
/tags/?tags=health&tags=doctor&tags=pharmacy
```

Response:

```json
{"tags": ["health", "doctor", "pharmacy"]}
```

---

✅ So in short:

* Function args = query params (if not in path).
* Type hints = auto validation.
* `Query()` = advanced constraints.

---

👉 Do you want me to show you how to combine **query params + path params** in one endpoint (e.g., `/users/{user_id}?active=true&page=2`)?
