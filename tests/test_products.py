import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import ValidationError
from models.products import Product, ProductCreate
from httpx import AsyncClient
from services.products import create_product


def test_create_product_missing_fields():
    """Test that creating a product with missing required fields raises validation errors."""
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(name=None, description=None, price=None, stock=None)
    
    errors = exc_info.value.errors()
    assert len(errors) == 3
    assert errors[0]["msg"].lower() == "input should be a valid string"
    assert errors[1]["msg"].lower() == "input should be a valid number"
    assert errors[2]["msg"].lower() == "input should be a valid integer"


def test_create_product_invalid_values():
    """Test that creating a product with invalid values raises validation errors."""
    max_name_length, max_desc_length = 255, 500
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            name="A" * (max_name_length + 1),
            description="A" * (max_desc_length + 1),
            price=0, stock=-1
        )
    
    errors = exc_info.value.errors()
    assert len(errors) == 4
    assert errors[0]["msg"].lower() == f"string should have at most {max_name_length} characters"
    assert errors[1]["msg"].lower() == f"string should have at most {max_desc_length} characters"
    assert errors[2]["msg"].lower() == "input should be greater than 0"
    assert errors[3]["msg"].lower() == "input should be greater than or equal to 0"


@pytest.mark.asyncio
async def test_create_product_success(db_session: AsyncSession):
    """Test successfully creating a product in the database."""
    product_data = ProductCreate(name="Test Product", description="Test description", price=100.0, stock=10)
    created_product = await create_product(db_session, product_data=product_data)

    assert created_product['id'] > 0
    assert created_product["name"] == "Test Product"
    assert created_product["description"] == "Test description"
    assert created_product["price"] == 100.0
    assert created_product["stock"] == 10
    
    stmt = select(Product).where(Product.id == created_product["id"])
    result = await db_session.execute(stmt)
    db_product = result.scalars().first()

    assert db_product, "Product was not created in the database."
    assert db_product.id > 0
    assert db_product.name == "Test Product"
    assert db_product.description == "Test description"
    assert db_product.price == 100.0
    assert db_product.stock == 10


@pytest.mark.asyncio
async def test_create_product_with_client(client: AsyncClient, db_session: AsyncSession):
    """Test API endpoint for creating a product."""
    product_data = {"name": "Test Product", "description": "Test Description", "price": 10.00, "stock": 30}
    response = await client.post("/products/", json=product_data)
    response_data = response.json()
    
    assert response.status_code == 201
    assert response_data['id'] > 0
    assert response_data['name'] == product_data['name']
    assert response_data['description'] == product_data['description']
    assert response_data['price'] == product_data['price']
    assert response_data['stock'] == product_data['stock']

    stmt = select(Product).where(Product.id == response_data["id"])
    result = await db_session.execute(stmt)
    db_product = result.scalars().first()
    
    assert db_product, "Product was not created in the database."
    assert db_product.id > 0
    assert db_product.name == product_data['name']
    assert db_product.description == product_data['description']
    assert db_product.price == product_data['price']
    assert db_product.stock == product_data['stock']

@pytest.mark.asyncio
async def test_create_product_invalid_data(client: AsyncClient):
    """Test API endpoint for handling invalid product creation data."""
    product_data = {"name": "T", "price": 0, "stock": -1}
    response = await client.post("/products/", json=product_data)
    response_data = response.json()
    
    assert response.status_code == 422
    assert len(response_data['detail']) == 3


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient):
    """Test retrieving a list of products via API."""
    response = await client.get("/products/")
    response_data = response.json()
    
    assert response.status_code == 200
    assert isinstance(response_data['data'], list)
    if response_data['data']:
        assert response_data['data'][0]['id'] > 0
