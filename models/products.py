from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Column, Relationship, Computed, DateTime, BigInteger, Field, func
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from models.orders import OrderBase, Order, OrderItem
from utils.helpers import get_current_timestamp

class ProductBase(SQLModel):
    name: str = Field(index=True, min_length=3, max_length=255)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(gt=0, description="Product price must be positive")
    stock: int = Field(ge=0, description="Stock must be non-negative")

class Product(ProductBase, table=True):
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

    order_links: List[OrderItem] = Relationship(back_populates="product")
    # orders: List[Order] = Relationship(back_populates="products", link_model=OrderItem)

    search_vector: str = Field(
        sa_column=Column(
            TSVECTOR,
            Computed(
                "to_tsvector('english', name || ' ' || coalesce(description, ''))",
                persisted=True
            )
        )
    )

    __table_args__ = (
        Index("idx_product_search", "search_vector", postgresql_using="gin"),
    )

class ProductRead(ProductBase):
    id: int = Product.id

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductOrderItemRead(SQLModel):
    product_id: int = Product.id
    product_name: str = Product.name
    quantity: int = OrderItem.quantity
    price: float = OrderItem.unit_price

class OrderWithProductRead(OrderBase):
    id: int = Order.id
    items: List[ProductOrderItemRead]
    created_at: datetime = Order.created_at

product_public_fields = [
    Product.id,
    Product.name,
    Product.price,
    Product.stock,
]