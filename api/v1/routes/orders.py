from fastapi import APIRouter
from utils.logger import logger

router = APIRouter()

@router.get("/")
async def get_orders():
    try:
        return {
            'current_page': 1,
            'page_size': 10,
            'total_records': 100,
            'total_pages': 10,
            'data': []
        }
    except Exception as e:
        logger.error(f"Exception in get_orders ==> {e}")