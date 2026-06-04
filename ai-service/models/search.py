from pydantic import BaseModel
from typing import List, Optional, Any


class AutosuggestIdentifier(BaseModel):
    uniqueIdentifier: str
    type: str
    name: str
    cityName: Optional[str] = None
    countryName: Optional[str] = None
    stateName: Optional[str] = None


class AutoSuggestPayload(BaseModel):
    autoSuggestKey: str


class AutoSuggestEntry(BaseModel):
    uniqueId: str
    type: str
    name: str
    cityName: Optional[str] = None
    stateName: Optional[str] = None
    countryName: Optional[str] = None


class AutoSuggestResponse(BaseModel):
    success: bool
    status: int
    message: str
    autoSuggestId: str
    autoSuggests: List[AutoSuggestEntry]


class RoomGuest(BaseModel):
    guestType: str = "ADT"


class Room(BaseModel):
    roomNo: int
    adultCount: int = 1
    childrenCount: int = 0
    guests: List[Any] = []


class HotelSearchPayload(BaseModel):
    autoSuggestId: str
    autosuggestIdentifier: AutosuggestIdentifier
    checkIn: str
    checkOut: str
    journeyType: str = "Domestic"
    pageIndex: Optional[int] = None
    pageSize: Optional[int] = None
    rooms: List[Room]
    travelType: str = "Business Travel"


# Alias for backward compatibility
HotelSearchRequest = HotelSearchPayload


class ProviderInfo(BaseModel):
    vendorName: Optional[str] = None
    providerHotelCode: Optional[str] = None
    fareType: Optional[str] = None
    totalFare: Optional[float] = None
    baseFare: Optional[float] = None
    taxes: Optional[float] = None
    additionalCharges: Optional[float] = None
    refundable: Optional[bool] = None
    boardBasis: List[Any] = []
    inPolicy: Optional[Any] = None
    outPolicyReasons: List[Any] = []
    paymentType: Optional[str] = None
    ruleName: Optional[str] = None
    outPolicyReasonKey: List[Any] = []


class HotelImageLink(BaseModel):
    size: Optional[str] = None
    providerHref: Optional[str] = None
    href: Optional[str] = None
    links: Optional[Any] = None


class HotelImage(BaseModel):
    caption: Optional[str] = None
    category: Optional[str] = None
    links: List[HotelImageLink] = []
    roomId: Optional[Any] = None


class HotelAddress(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    code: Optional[str] = None
    destinationCode: Optional[str] = None
    state: Optional[str] = None
    stateCode: Optional[str] = None
    country: Optional[str] = None
    countryCode: Optional[str] = None
    postalCode: Optional[str] = None


class HotelContact(BaseModel):
    address: Optional[HotelAddress] = None
    phones: Optional[Any] = None


class HotelFacility(BaseModel):
    id: Optional[str] = None
    groupId: Optional[str] = None
    groupName: Optional[str] = None
    name: Optional[str] = None
    link: Optional[str] = None


class SearchHotelResult(BaseModel):
    vervotechHotelId: Optional[str] = None
    name: Optional[str] = None
    brandName: Optional[str] = None
    chainName: Optional[str] = None
    heroImage: Optional[str] = None
    images: List[HotelImage] = []
    starRating: Optional[str] = None
    fareType: List[str] = []
    isTCRecommended: Optional[bool] = None
    overallMinRate: Optional[float] = None
    overallMaxRate: Optional[float] = None
    providerInfo: List[ProviderInfo] = []
    facilities: List[HotelFacility] = []
    currency: Optional[str] = None
    propertyType: Optional[str] = None
    contact: Optional[HotelContact] = None


class HotelSearchData(BaseModel):
    searchKey: Optional[str] = None
    autoSuggestId: Optional[str] = None
    page: Optional[int] = None
    limit: Optional[int] = None
    minRate: Optional[float] = None
    maxRate: Optional[float] = None
    minStarRating: Optional[int] = None
    maxStarRating: Optional[int] = None
    cacheKey: Optional[str] = None
    vervotechHotelCount: Optional[int] = None
    hotels: List[SearchHotelResult] = []
    inprogress: Optional[bool] = None


class HotelSearchResponse(BaseModel):
    success: bool
    message: str
    status: int
    data: HotelSearchData


class BackgroundStatusRequest(BaseModel):
    autoSuggestId: str
    cacheKey: str
    searchKey: str


class BackgroundStatusData(BaseModel):
    status: int
    inProgress: bool
    cacheKey: str


class BackgroundStatusResponse(BaseModel):
    success: bool
    status: int
    message: str
    data: BackgroundStatusData


class SearchByPollRequest(BaseModel):
    autoSuggestId: str
    cacheKey: str
    capping_reached: bool = False
    checkIn: str
    checkOut: str
    hotelReceived: int = 0
    isSearchResultsProcessed: bool = True
    pageIndex: int = 1
    pageSize: int = 300
    searchKey: str
