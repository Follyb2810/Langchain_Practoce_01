from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/mydb"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Base.metadata.create_all(bind=engine)

# # Insert example
# db = SessionLocal()
# new_user = User(name="Alice")
# db.add(new_user)
# db.commit()
# db.refresh(new_user)
# print(new_user.id, new_user.name)
# db.close()
