import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models.products import ProductCreate
from models.orders import Order, OrderCreate, OrderItemCreate, OrderStatus
from services.products import create_product
from services.orders import create_order
from utils.exceptions import ValidationException


@pytest.mark.asyncio
async def test_create_order_success(db_session: AsyncSession):
    """Test successful order creation."""
    # Create products for order
    products = [
        {
            "name": "Product One",
            "description": "Product One Description",
            "price": 10,
            "stock": 10
        },
        {
            "name": "Product Two",
            "description": "Product Two Description",
            "price": 20,
            "stock": 5
        }
    ]

    created_products = []
    for product in products:
        product_data = ProductCreate(**product)
        created_product = await create_product(db_session, product_data=product_data)

        created_products.append(created_product)

    order_items = []
    total_price = 0
    for product in created_products:
        order_item = OrderItemCreate(product_id=product['id'], quantity=product['stock'])
        total_price += order_item.quantity * product['price']
        order_items.append(order_item)

    order_data = OrderCreate(items=order_items)
    created_order = await create_order(db_session, order_data=order_data)

    assert created_order['id'] is not None
    assert created_order["total_price"] == total_price
    assert len(created_order["items"]) == len(created_products)
    assert created_order["items"][0]["product_id"] == created_products[0]['id']
    assert created_order["items"][0]["quantity"] == created_products[0]['stock']

    stmt = select(Order).where(Order.id == created_order["id"])
    result = await db_session.execute(stmt)
    db_order = result.scalars().first()

    if not db_order:
        pytest.fail("Order was not created in the database.")

    assert db_order.id is not None
    assert db_order.total_price == total_price
    assert db_order.status == OrderStatus.PENDING


@pytest.mark.asyncio
async def test_create_order_insufficient_stock(db_session: AsyncSession):
    """Test creating an order with insufficient stock should fail."""
    # Create products for order
    product_raw_data = {
        "name": "Product One",
        "description": "Product One Description",
        "price": 10,
        "stock": 10
    }
    product_data = ProductCreate(**product_raw_data)
    created_product = await create_product(db_session, product_data=product_data)

    order_item = OrderItemCreate(product_id=created_product['id'], quantity=created_product['stock'] + 1)
    order_data = OrderCreate(items=[order_item])

    exc_msg = f"Insufficient stock for Product ID {created_product['id']}. Requested: {order_item.quantity}, Available: {created_product['stock']}"
    with pytest.raises(ValidationException, match=exc_msg):
        await create_order(db_session, order_data=order_data)

