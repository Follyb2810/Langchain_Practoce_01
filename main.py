from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from model.product_model import ProductModel, ProductSchema
from model.user_model import UserModel, UserSchema
from db import engine, Base, get_db, SessionLocal
from seed import seed_data

Base.metadata.create_all(bind=engine)

products: List[ProductModel] = [
    ProductModel(
        id=1, label="Apple", price=1.2, quantity=10, description="Fresh red apples"
    ),
    ProductModel(id=2, label="Banana", price=0.5, quantity=25),
    ProductModel(id=3, label="Carrot"),
]


def int_db():
    db = SessionLocal()

    if db.query(ProductSchema).count() == 0:
        for pd in products:
            db.add(ProductSchema(**pd.model_dump()))

    db.commit()
    db.close()


int_db()

seed_data()

app = FastAPI()


@app.get("/")
def greet():
    return {"message": "Hello world"}


@app.get("/products", response_model=List[ProductModel])
def get_all_products(db: Session = Depends(get_db)):
    return db.query(ProductSchema).all()


@app.get("/product/{id}", response_model=ProductModel)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(ProductSchema).filter(ProductSchema.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"No product with id {id}")
    return product


@app.post("/products", response_model=ProductModel)
def create_product(product: ProductModel, db: Session = Depends(get_db)):
    new_product = ProductSchema(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.put("/product/{id}", response_model=ProductModel)
def update_product(id: int, updated: ProductModel, db: Session = Depends(get_db)):
    product = db.query(ProductSchema).filter(ProductSchema.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"No product with id {id}")

    for field, value in updated.model_dump().items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@app.put("/product_test/{id}", response_model=ProductModel)
def update_product(id: int, updated: ProductModel):
    # for i in range(len(products)):
    #     if products[i].id == id:
    #         products[i] == updated
    #         return products[i]
    for index, pd in enumerate(products):
        if pd.id == id:
            products[index] = ProductModel(id=id, label=updated.label)
            return products[index]
    raise HTTPException(status_code=404, detail=f"No product with id {id}")


@app.delete("/product/{id}")
def delete_product(id: int):

    for index, pd in enumerate(products):
        if pd.id == id:
            deleted = products.pop(index)
            return {"message": f"Product {id} deleted", "product": deleted}
    raise HTTPException(status_code=404, detail=f"No product with id {id}")


@app.get("/products_test/sum_ids")
def sum_ids():
    return {"sum_ids": sum(p.id for p in products)}


@app.get("/products_test/count")
def count_products():
    return {"count": len(products)}


@app.get("/products_test/search")
def search_products(label: str):
    return [p for p in products if p.label == label]


@app.delete("/product/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(ProductSchema).filter(ProductSchema.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"No product with id {id}")

    db.delete(product)
    db.commit()
    return {"message": f"Product {id} deleted"}


@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    products = db.query(ProductSchema).all()
    users = db.query(UserSchema).all()
    return {
        "products": [ProductModel.model_validate(p) for p in products],
        "users": [UserModel.model_validate(u) for u in users],
    }


