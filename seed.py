from db import SessionLocal
from model.product_model import ProductSchema
from model.user_model import UserSchema


def seed_data():
    db = SessionLocal()
    try:

        if db.query(ProductSchema).count() == 0:
            sample_products = [
                ProductSchema(
                    label="Apple",
                    price=1.2,
                    quantity=10,
                    description="Fresh red apples",
                ),
                ProductSchema(label="Banana", price=0.5, quantity=25),
                ProductSchema(
                    label="Carrot",
                    price=0.8,
                    quantity=30,
                    description="Organic carrots",
                ),
            ]
            db.add_all(sample_products)

        if db.query(UserSchema).count() == 0:
            sample_users = [
                UserSchema(username="alice", email="alice@example.com"),
                UserSchema(username="bob", email="bob@example.com"),
            ]
            db.add_all(sample_users)

        db.commit()
        print("✅ Seed data inserted")
    finally:
        db.close()


