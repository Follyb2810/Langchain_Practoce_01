from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, Float
from db import Base


class ProductSchema(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False, default=0.0)
    description = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False, default=0)


class ProductModel(BaseModel):
    id: Optional[int] = None
    label: str
    description: Optional[str] = None
    price: float = 0.0
    quantity: int = 0

    model_config = {"from_attributes": True}
    # class Config:
    #     orm_mode = True
