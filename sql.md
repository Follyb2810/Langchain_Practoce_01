## 🔑 **Session methods**

These are used on your `SessionLocal()` instance (`db` in your code):

* **`db.add(obj)`** → add a single object.
* **`db.add_all([obj1, obj2, ...])`** → add multiple objects.
* **`db.commit()`** → save changes to the database.
* **`db.rollback()`** → undo uncommitted changes if something fails.
* **`db.refresh(obj)`** → reload an object’s state from the DB (e.g., after an insert with auto-generated ID).
* **`db.close()`** → close the session.

---

## 🔑 **Query methods**

Called when you do `db.query(Model)`:

* **`.all()`** → fetch all rows.
* **`.first()`** → fetch the first row (or `None`).
* **`.get(id)`** → fetch by primary key.
* **`.filter(Model.column == value)`** → filter results.
* **`.filter_by(column=value)`** → shorthand filter.
* **`.order_by(Model.column)`** → order results.
* **`.count()`** → count rows.
* **`.limit(n)`** → limit number of results.
* **`.offset(n)`** → skip n rows.
* **`.join(OtherModel)`** → join with another table.
* **`.delete()`** → delete rows (when used with `.filter()`).

---

## 🔑 **Model object methods**

For instances of your models (like `ProductSchema` or `UserSchema`):

* **`.id` (or any attribute)** → access a column.
* **`.dict()`** (if using Pydantic model, not SQLAlchemy directly) → convert to dictionary.
* **`repr(obj)`** (if you define `__repr__`) → debug-friendly printing.

---

## 🔑 **Examples**

```python
# Insert
product = ProductSchema(label="Mango", price=1.5, quantity=10)
db.add(product)
db.commit()
db.refresh(product)   # now product.id will be available

# Query
all_products = db.query(ProductSchema).all()
first_product = db.query(ProductSchema).first()
one_product = db.query(ProductSchema).get(1)

# Filter
apples = db.query(ProductSchema).filter(ProductSchema.label == "Apple").all()

# Update
product = db.query(ProductSchema).get(1)
product.price = 2.0
db.commit()

# Delete
db.query(ProductSchema).filter(ProductSchema.label == "Banana").delete()
db.commit()
```
