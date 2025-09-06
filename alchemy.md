Great question 👍 Relationships in **SQLAlchemy** are how you tell the ORM about foreign key connections between tables — so you can navigate objects instead of writing manual joins.

---

## 🔹 Basics of Relationships in SQLAlchemy

### 1. One-to-Many (most common)

Example: A **User** can have many **Appointments**.

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)

    # one-to-many: back_populates creates two-way access
    appointments = relationship("Appointment", back_populates="user")


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    details = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="appointments")
```

Usage:

```python
u = session.query(User).first()
print(u.appointments)   # list of appointments

a = session.query(Appointment).first()
print(a.user.full_name) # get the user of the appointment
```

---

### 2. One-to-One

Just a one-to-many with `uselist=False`.

Example: Each **User** has **one Profile**.

```python
class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    bio = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="profile", uselist=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)

    profile = relationship("Profile", back_populates="user", uselist=False)
```

---

### 3. Many-to-Many

Example: Users can have many **Specialities**, and a Speciality can belong to many Users.
You use an **association table**.

```python
from sqlalchemy import Table

user_speciality = Table(
    "user_speciality",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("speciality_id", ForeignKey("specialities.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)

    specialities = relationship("Speciality", secondary=user_speciality, back_populates="users")

class Speciality(Base):
    __tablename__ = "specialities"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    users = relationship("User", secondary=user_speciality, back_populates="specialities")
```

---

## 🔹 How it applies to your schema

In your `User` model:

* `relationship` (kin) → could be just a `String` (what you already have).
* But if you want **multiple kin contacts** per user → you’d model a `Kin` table with a **One-to-Many** relationship.

Example:

```python
class Kin(Base):
    __tablename__ = "kins"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    phone = Column(String)
    relationship = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="kins")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)

    kins = relationship("Kin", back_populates="user")
```

Now you can do:

```python
user = session.query(User).first()
for kin in user.kins:
    print(kin.full_name, kin.relationship)
```
clear