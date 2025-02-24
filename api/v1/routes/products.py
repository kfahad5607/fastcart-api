from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.sql import get_session
from models.common import PaginationResponse
from models.products import ProductCreate, ProductRead
from services.products import get_products, create_product
from utils.exceptions import BaseAppException, ValidationException
from utils.logger import logger


router = APIRouter()

@router.get("/", response_model=PaginationResponse[ProductRead])
async def handle_get_products(
    session: AsyncSession=Depends(get_session),
    query: Optional[str] = Query(default=""),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=101),
    sort_by: Optional[str] = Query(None)
):
    try:
        return await get_products(session, query=query, page=page, page_size=page_size, sort_by=sort_by)
    except ValidationException as e:
        raise
    except Exception as e:
        raise BaseAppException("Could not get the products. Please try again later.") from e

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductRead)
async def handle_create_product(product_data: ProductCreate, session: AsyncSession=Depends(get_session)):
    try:
        return await create_product(session, product_data=product_data)
    except Exception as e:
        logger.error(f"ERRRORR  ==> {type(e)=}")
        raise BaseAppException("Could not create the product. Please try again later.") from e