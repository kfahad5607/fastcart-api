from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlmodel import SQLModel, Column, Relationship, DateTime, BigInteger, Field, func, Enum as SQLAlchemyEnum
from models.products import Product
from utils.helpers import get_current_timestamp

class OrderStatus(str, Enum):
    PENDING = "pending"
    CANCELED = "canceled"
    COMPLETED = "completed"

class OrderItem(SQLModel, table=True):
    order_id: Optional[int] = Field(default=None, foreign_key="order.id", primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id", primary_key=True)
    quantity: int = Field(ge=1, description="Quantity must be at least 1")
    unit_price: float = Field(gt=0, description="Price per unit at time of order")

class OrderBase(SQLModel):
    total_price: float = Field(default=0, description="Auto-calculated total order price")
    status: OrderStatus = Field(sa_column=Column(SQLAlchemyEnum(OrderStatus)), default=OrderStatus.PENDING)

class Order(OrderBase, table=True):
    id: int = Field(default=None, sa_column=Column(BigInteger, autoincrement=True, primary_key=True))
    products: List[Product] = Relationship(back_populates="orders", link_model=OrderItem)
    created_at: datetime = Field(default_factory=get_current_timestamp, sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    ))
    updated_at: datetime = Field(default_factory=get_current_timestamp, sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=func.now()
    ))


class OrderPublic(OrderBase):
    id: int = Order.id

class OrderCreate(OrderBase):
    pass

class OrderUpdate(OrderBase):
    pass