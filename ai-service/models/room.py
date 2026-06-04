from pydantic import BaseModel
from typing import Any, List, Optional


class RoomDetailsRequest(BaseModel):
    autoSuggestId: str
    filterBySupplier: List[str] = []
    hotelId: str
    searchKey: str


class RoomDetailsResponse(BaseModel):
    success: bool
    status: int
    message: str
    autoSuggestId: Optional[str] = None
    searchKey: Optional[str] = None
    roomData: Any = None
