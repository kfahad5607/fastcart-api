from typing import TypeVar, Generic, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginationResponse(BaseModel, Generic[T]):
    current_page: int
    page_size: int
    total_records: int
    total_pages: int
    data: List[T]
