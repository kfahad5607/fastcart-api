from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List
from sqlmodel import SQLModel, Column, DateTime, BigInteger, Enum as SQLAlchemyEnum, Relationship, ForeignKey, Field, func
from utils.helpers import get_current_timestamp

if TYPE_CHECKING:
    from models.products import Product

class OrderStatus(str, Enum):
    PENDING = "pending"
    CANCELED = "canceled"
    COMPLETED = "completed"

class OrderItem(SQLModel, table=True):
    order_id: int = Field(foreign_key="order.id", primary_key=True, ondelete="CASCADE")
    product_id: int = Field(foreign_key="product.id", primary_key=True, ondelete="CASCADE")
    quantity: int = Field(gt=0, description="Quantity must be at least 1")
    unit_price: float = Field(gt=0, description="Price per unit at time of order")

    product: "Product" = Relationship(back_populates="order_links")
    order: "Order" = Relationship(back_populates="product_links")

class OrderBase(SQLModel):
    total_price: float = Field(gt=0, description="Total order price")
    status: OrderStatus = Field(sa_column=Column(SQLAlchemyEnum(OrderStatus)), default=OrderStatus.PENDING)

class Order(OrderBase, table=True):
    id: int = Field(default=None, sa_column=Column(BigInteger, autoincrement=True, primary_key=True))
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

    product_links: List[OrderItem] = Relationship(back_populates="order")

class OrderItemCreate(SQLModel):
    product_id: int = Field(gt=0, description="Product ID must be at least 1")
    quantity: int = Field(gt=0, description="Quantity must be at least 1")

class OrderCreate(SQLModel):    
    items: List[OrderItemCreate]

class OrderRead(OrderBase):
    id: int = Order.id

class OrderUpdate(OrderBase):
    pass