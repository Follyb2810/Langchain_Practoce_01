Got it 👍 — you’re asking about **common Python type hints** (from `typing`) and especially about the new **`Annotated`** type that’s widely used in **FastAPI** and modern Python (PEP 593).

---

# 🔹 Common Type Hints in Python

Here are the ones you’ll use most often:

### 1. **Basic types**

```python
name: str
age: int
height: float
is_active: bool
```

---

### 2. **Optional (nullable) values**

```python
from typing import Optional

middle_name: Optional[str]  # means str | None
```

Since Python 3.10, you can also write:

```python
middle_name: str | None
```

---

### 3. **Lists, Tuples, Dicts**

```python
from typing import List, Dict, Tuple

tags: List[str]            # ["health", "doctor"]
coordinates: Tuple[float,float]  # (12.3, 45.6)
settings: Dict[str, str]   # {"theme": "dark"}
```

Modern syntax:

```python
tags: list[str]
coordinates: tuple[float, float]
settings: dict[str, str]
```

---

### 4. **Union**

```python
from typing import Union

id: Union[int, str]   # could be 1 or "abc"
```

Modern syntax:

```python
id: int | str
```

---

### 5. **Any (don’t check type)**

```python
from typing import Any

data: Any
```

---

### 6. **Callable (functions)**

```python
from typing import Callable

operation: Callable[[int, int], int]  # function that takes 2 ints and returns int
```

---

### 7. **Iterable / Generator**

```python
from typing import Iterable, Generator

numbers: Iterable[int]   # any iterable of ints
stream: Generator[str, None, None]  # generator of strings
```

---

### 8. **TypedDict & NamedTuple**

For structured dict-like objects:

```python
from typing import TypedDict

class UserDict(TypedDict):
    id: int
    name: str
```

---

# 🔹 Annotated (PEP 593)

`Annotated` lets you **add metadata to type hints**.
FastAPI uses it heavily for validation, documentation, and dependency injection.

---

### 1. Basic usage

```python
from typing import Annotated

age: Annotated[int, "must be positive"]
```

Here, `age` is an `int`, but with extra metadata (`"must be positive"`).
Libraries like FastAPI can use this metadata.

---

### 2. FastAPI Example

```python
from fastapi import Query
from typing import Annotated

@app.get("/items/")
def read_items(
    q: Annotated[str | None, Query(min_length=3, max_length=50)] = None
):
    return {"q": q}
```

* `q` is a query parameter
* Type: `str | None`
* Metadata: validation (`min_length`, `max_length`)

---

### 3. Another Example with Path

```python
from fastapi import Path

@app.get("/users/{user_id}")
def get_user(user_id: Annotated[int, Path(gt=0)]):
    return {"user_id": user_id}
```

Here:

* Type: `int`
* Constraint: must be > 0

---

### 4. Multiple metadata

```python
from typing import Annotated
from fastapi import Query

score: Annotated[int, Query(ge=0, le=100), "percentage"]
```

# 🔹 Generics Basics

### 1. `TypeVar`

```python
from typing import TypeVar, List

T = TypeVar("T")  # a generic type variable

def first_item(items: List[T]) -> T | None:
    return items[0] if items else None
```

Usage:

```python
first_item([1, 2, 3])        # inferred as int
first_item(["a", "b", "c"])  # inferred as str
```

---

### 2. Constraining `TypeVar`

```python
from typing import TypeVar

Number = TypeVar("Number", int, float)

def double(x: Number) -> Number:
    return x * 2
```

Here, `Number` can only be `int` or `float`.

---

### 3. Generic Classes

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, content: T):
        self.content = content

    def get(self) -> T:
        return self.content
```

Usage:

```python
int_box = Box 
str_box = Box[str]("hello")

print(int_box.get())  # int
print(str_box.get())  # str
```

---

### 4. Multiple TypeVars

```python
from typing import TypeVar, Generic

K = TypeVar("K")
V = TypeVar("V")

class KeyValue(Generic[K, V]):
    def __init__(self, key: K, value: V):
        self.key = key
        self.value = value
```

Usage:

```python
kv = KeyValue[str, int]("age", 30)
```

---

### 5. Protocols (structural typing with generics)

```python
from typing import Protocol, TypeVar

T = TypeVar("T")

class SupportsLen(Protocol):
    def __len__(self) -> int: ...

def total_length(items: list[T]) -> int:
    return sum(len(item) for item in items if isinstance(item, SupportsLen))
```

---

# 🔹 `Annotated` + Generics (FastAPI / Pydantic v2)

You can even combine **Generics + Annotated**:

```python
from typing import Generic, TypeVar, Annotated
from fastapi import Query

T = TypeVar("T")

def paginated_query(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10
):
    return {"page": page, "size": size}
```

And for **Pydantic Models**:

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T
    success: bool = True
```

Usage:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

res = Response[User](data=User(id=1, name="Eniola"))
```

