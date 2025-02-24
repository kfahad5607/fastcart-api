import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from httpx import AsyncClient
from models.products import Product, ProductCreate
from models.orders import Order, OrderCreate, OrderItemCreate, OrderStatus
from services.products import create_product
from services.orders import create_order
from utils.exceptions import ValidationException


@pytest.mark.asyncio
async def test_create_order_success(db_session: AsyncSession):
    """Test successful order creation with valid products and quantities."""
    # Create test products
    products = [
        {"name": "Product One", "description": "Product One Description", "price": 10, "stock": 10},
        {"name": "Product Two", "description": "Product Two Description", "price": 20, "stock": 5},
    ]

    created_products = [await create_product(db_session, ProductCreate(**p)) for p in products]

    order_items = []
    total_price = 0
    for product in created_products:
        order_item = OrderItemCreate(product_id=product['id'], quantity=product['stock'])
        total_price += order_item.quantity * product['price']
        order_items.append(order_item)

    order_data = OrderCreate(items=order_items)
    created_order = await create_order(db_session, order_data=order_data)

    assert created_order['id'] > 0
    assert created_order["total_price"] == total_price
    assert len(created_order["items"]) == len(created_products)
    assert created_order["items"][0]["product_id"] == created_products[0]['id']
    assert created_order["items"][0]["quantity"] == created_products[0]['stock']

    stmt = select(Order).where(Order.id == created_order["id"])
    result = await db_session.execute(stmt)
    db_order = result.scalars().first()

    assert db_order, "Order was not created in the database."
    assert db_order.id > 0
    assert db_order.total_price == total_price
    assert db_order.status == OrderStatus.PENDING


@pytest.mark.asyncio
async def test_create_order_insufficient_stock(db_session: AsyncSession):
    """Test order creation failure when requested quantity exceeds available stock."""
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

    expected_msg = (
        f"Insufficient stock for Product ID {created_product['id']}. "
        f"Requested: {order_item.quantity}, Available: {created_product['stock']}"
    )

    with pytest.raises(ValidationException, match=expected_msg):
        await create_order(db_session, order_data=order_data)


@pytest.mark.asyncio
async def test_create_order_with_client_success(client: AsyncClient, db_session: AsyncSession):
    """Test successful order creation using the API client."""
    stmt = select(Product).where(Product.stock > 0).limit(1)
    db_product = (await db_session.execute(stmt)).scalars().first()

    assert db_product, "Product was not found in the database."

    order_data = {"items": [{"product_id": db_product.id, "quantity": db_product.stock}]}
    response = await client.post("orders/", json=order_data)
    response_data = response.json()
    total_price = db_product.price * db_product.stock

    assert response.status_code == 201
    assert response_data['id'] > 0
    assert response_data["total_price"] == total_price
    assert len(response_data["items"]) == len(order_data['items'])
    assert response_data["items"][0]["product_id"] == db_product.id
    assert response_data["items"][0]["quantity"] == db_product.stock

    stmt = select(Order).where(Order.id == response_data["id"])
    result = await db_session.execute(stmt)
    db_order = result.scalars().first()

    assert db_order, "Order was not created in the database."
    assert db_order.id > 0
    assert db_order.total_price == total_price
    assert db_order.status == OrderStatus.PENDING

@pytest.mark.asyncio
async def test_create_order_with_invalid_product(client: AsyncClient):
    """Test order creation failure when product ID does not exist."""
    order_data = {"items": [{"product_id": 999999, "quantity": 10}]}
    response = await client.post("orders/", json=order_data)

    assert response.status_code == 400
    assert response.json()['error'] == "Products not found for IDs: 999999"


@pytest.mark.asyncio
async def test_create_order_with_insufficient_stock_client(client: AsyncClient, db_session: AsyncSession):
    """Test order creation failure when requested quantity exceeds available stock using API client."""
    stmt = select(Product).limit(1)
    db_product = (await db_session.execute(stmt)).scalars().first()

    assert db_product, "Product was not found in the database."

    order_data = {"items": [{"product_id": db_product.id, "quantity": db_product.stock + 1}]}
    response = await client.post("orders/", json=order_data)

    expected_msg = (
        f"Insufficient stock for Product ID {db_product.id}. "
        f"Requested: {db_product.stock + 1}, Available: {db_product.stock}"
    )

    assert response.status_code == 400
    assert response.json()['error'] == expected_msg


@pytest.mark.asyncio
async def test_create_order_with_empty_items(client: AsyncClient):
    """Test order creation failure when no items are provided."""
    response = await client.post("orders/", json={"items": []})

    assert response.status_code == 400
    assert "Order must contain at least one item" in response.json()['error']


@pytest.mark.asyncio
async def test_create_order_with_negative_quantity(client: AsyncClient, db_session: AsyncSession):
    """Test order creation failure when item quantity is negative."""
    stmt = select(Product).limit(1)
    db_product = (await db_session.execute(stmt)).scalars().first()

    assert db_product, "Product was not found in the database."

    order_data = {"items": [{"product_id": db_product.id, "quantity": -5}]}
    response = await client.post("orders/", json=order_data)

    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == "Input should be greater than 0"
