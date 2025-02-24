from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.sql import get_session
from models.orders import OrderCreate
from models.products import OrderWithProductRead
from services.orders import create_order
from utils.exceptions import BaseAppException, ValidationException

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderWithProductRead)
async def handle_create_order(order_data: OrderCreate, session: AsyncSession=Depends(get_session)):
    try:
        return await create_order(session, order_data=order_data)
    except ValidationException as e:
        raise
    except Exception as e:
        await session.rollback()
        raise BaseAppException("Could not create the order. Please try again later.") from e