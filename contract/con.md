Perfect 👌 let’s build a **reusable CRUD utility** for both `Product` and `User`.
This way you don’t repeat yourself in your FastAPI routes — you’ll just call the CRUD class methods.

---

## 📂 `crud/base.py` → generic reusable CRUD class

```python
from sqlalchemy.orm import Session
from typing import Generic, Type, TypeVar, List, Optional

# Type variables for models
ModelType = TypeVar("ModelType")

class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).get(id)

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
```

---

## 📂 `crud/product.py`

```python
from crud.base import CRUDBase
from model.product_model import ProductSchema

class CRUDProduct(CRUDBase[ProductSchema]):
    pass

product_crud = CRUDProduct(ProductSchema)
```

---

## 📂 `crud/user.py`

```python
from crud.base import CRUDBase
from model.user_model import UserSchema

class CRUDUser(CRUDBase[UserSchema]):
    pass

user_crud = CRUDUser(UserSchema)
```

---

## 📂 Example usage in your FastAPI routes

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
from crud.product import product_crud
from crud.user import user_crud
from model.product_model import ProductModel
from model.user_model import UserModel
from typing import List

app = FastAPI()

# Dependency: open a session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/products", response_model=List[ProductModel])
def get_products(db: Session = Depends(get_db)):
    return product_crud.get_all(db)


@app.post("/products", response_model=ProductModel)
def create_product(product: ProductModel, db: Session = Depends(get_db)):
    return product_crud.create(db, product.dict())


@app.get("/users", response_model=List[UserModel])
def get_users(db: Session = Depends(get_db)):
    return user_crud.get_all(db)


@app.post("/users", response_model=UserModel)
def create_user(user: UserModel, db: Session = Depends(get_db)):
    return user_crud.create(db, user.dict())
```

---

✅ Now you have a **generic CRUD base class** you can extend for any model.
For example:

* `product_crud.get_all(db)`
* `user_crud.create(db, {...})`

Each schema (`ProductSchema`, `UserSchema`) plugs in automatically.

