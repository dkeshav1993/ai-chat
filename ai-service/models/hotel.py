from pydantic import BaseModel
from typing import Any, Optional


class HotelDetailsRequest(BaseModel):
    hotelId: str
    searchKey: str


class HotelDetailsResponse(BaseModel):
    success: bool
    status: int
    message: str
    searchKey: Optional[str] = None
    hotelData: Any = None
