from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import asc, desc, nulls_first, nulls_last
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, text, func
from db.sql import get_session
from models.common import PaginationResponse
from models.products import Product, ProductCreate, ProductRead, product_public_fields
from utils.exceptions import BaseAppException, ValidationException
from utils.logger import logger
from utils.helpers import get_total_pages


router = APIRouter()

def build_sorting_expression(sort_by: Optional[str], model: Product, allowed_columns: List[str]) -> List:
    """Helper to handle sorting logic."""
    sort_expressions = []
    if sort_by:
        sort_fields = sort_by.split(",")

        for field in sort_fields:
            desc_order = field.startswith("-")
            col_name = field.lstrip("-")

            if col_name not in allowed_columns:
                raise ValidationException(message=f"Invalid sort field: {col_name}")

            sort_expr = nulls_last(desc(getattr(model, col_name))) if desc_order else nulls_first(asc(getattr(model, col_name)))
            sort_expressions.append(sort_expr)

    sort_expressions.append(desc(model.created_at))

    return sort_expressions

def build_query_filter(model: Product) -> Optional[str]:
    """Helper to handle query-based filtering logic."""
    query_condition = model.search_vector.op('@@')(text("plainto_tsquery('english', :query)"))
    return query_condition

@router.get("/", response_model=PaginationResponse[ProductRead])
async def get_products(
    session: AsyncSession=Depends(get_session),page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=101),
    query: Optional[str] = Query(default=""),
    sort_by: Optional[str] = Query(None)
):
    try:
        query = query.strip()
        offset = (page - 1) * page_size
        stmt = select(*product_public_fields)
        total_count_stmt = select(func.count()).select_from(Product)

        if query:
            where_clause = build_query_filter(Product)

            stmt = stmt.where(where_clause).params(query=query)
            total_count_stmt = total_count_stmt.where(where_clause).params(query=query)

        sort_expressions = build_sorting_expression(sort_by=sort_by, model=Product, allowed_columns=['name'])
        stmt = stmt.order_by(*sort_expressions).limit(page_size).offset(offset)

        results = await session.execute(stmt)

        # Get Total Products
        total_results = await session.execute(total_count_stmt)
        total_count = total_results.scalar()

        products = results.mappings().all()

        return {
            'current_page': page,
            'page_size': page_size,
            'total_records': total_count,
            'total_pages': get_total_pages(total_count, page_size),
            'data': products
        }
    
    except ValidationException as e:
        raise
    except Exception as e:
        logger.error(f"Exception in get_products ==> {e}")
        raise BaseAppException("Could not get the products. Please try again later.") from e

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductRead)
async def create_product(product_create: ProductCreate, session: AsyncSession=Depends(get_session)):
    try:
        product_create.name = product_create.name.strip()
        if product_create.description:
            product_create.description = product_create.description.strip()

        new_product = Product(**product_create.model_dump())
        session.add(new_product)
        await session.commit()

        new_product_data = {field.name: getattr(new_product, field.name) for field in product_public_fields}

        return new_product_data

    except Exception as e:
        logger.error(f"Exception in create_product ==> {e}")
        await session.rollback()
        raise BaseAppException("Could not create the product. Please try again later.") from e