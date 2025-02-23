import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import ValidationError
from models.products import Product, ProductCreate
from services.products import create_product

def test_create_product_missing_fields():
    """Test creating a product with missing fields should fail."""
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            name=None,
            description=None,
            price=None,
            stock=None
        )

    errors = exc_info.value.errors()
    assert len(errors) == 3

    assert errors[0]["msg"].lower() == "input should be a valid string"
    assert errors[1]["msg"].lower() == "input should be a valid number"
    assert errors[2]["msg"].lower() == "input should be a valid integer"

def test_create_product_invalid_values():
    """Test creating a product with missing fields should fail."""
    max_name_length = 255
    max_description_length = 500

    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            name="A" * (max_name_length + 1),
            description="A" * (max_description_length + 1),
            price=0,
            stock=-1
        )

    errors = exc_info.value.errors()
    assert len(errors) == 4

    assert errors[0]["msg"].lower() == f"string should have at most {max_name_length} characters"
    assert errors[1]["msg"].lower() == f"string should have at most {max_description_length} characters"
    assert errors[2]["msg"].lower() == "input should be greater than 0"
    assert errors[3]["msg"].lower() == "input should be greater than or equal to 0"

@pytest.mark.asyncio
async def test_create_product_success(db_session: AsyncSession):
    """Test creating a product in the database."""
    product_data = ProductCreate(
        name="Test Product",
        description="This is a test product",
        price=100.0,
        stock=10
    )

    created_product = await create_product(db_session, product_data=product_data)

    assert created_product['id'] is not None
    assert created_product["name"] == "Test Product"
    assert created_product["description"] == "This is a test product"
    assert created_product["price"] == 100.0
    assert created_product["stock"] == 10

    stmt = select(Product).where(Product.id == created_product["id"])
    result = await db_session.execute(stmt)
    db_product = result.scalars().first()

    if not db_product:
        pytest.fail("Product was not created in the database.")

    assert db_product.id is not None
    assert db_product.name == "Test Product"
    assert db_product.description == "This is a test product"
    assert db_product.price == 100.0
    assert db_product.stock == 10
