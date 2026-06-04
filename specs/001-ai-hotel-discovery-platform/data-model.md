# Data Model: AI-Powered Hotel Discovery Platform (NexTrip AI)

**Phase**: 1 — Design
**Date**: 2026-05-23
**Source**: `api/Hotel-Search-doc.md`, `specs/001-ai-hotel-discovery-platform/spec.md`

---

## 1. MySQL Schema (Flyway-managed)

### `search_history` (V1 Migration)

Stores one record per hotel search event. Written asynchronously after search intent extraction.

```sql
-- db/migrations/V1__create_search_history.sql

CREATE TABLE search_history (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id      VARCHAR(64)     NOT NULL,
    destination     VARCHAR(255)    NOT NULL,
    destination_type VARCHAR(32)   NOT NULL,           -- e.g. "CITY", "HOTEL", "AREA"
    unique_identifier VARCHAR(64)  NOT NULL,           -- autoSuggest uniqueId
    check_in        DATE            NOT NULL,
    check_out       DATE            NOT NULL,
    adult_count     TINYINT UNSIGNED NOT NULL DEFAULT 1,
    child_count     TINYINT UNSIGNED NOT NULL DEFAULT 0,
    room_count      TINYINT UNSIGNED NOT NULL DEFAULT 1,
    auto_suggest_id VARCHAR(64)     NULL,              -- autoSuggestId from AutoSuggest API
    search_key      VARCHAR(64)     NULL,              -- searchKey from Search API (if obtained)
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**Future extension notes**:
- `traveller` entity → new Flyway migration `V2__create_traveller.sql`
- `booking` entity → `V3__create_booking.sql`
- Both follow same Flyway-first discipline. No `ALTER TABLE` outside migrations.

---

## 2. Redis Data Structures

### Token Cache

| Key | Type | TTL | Value |
|---|---|---|---|
| `traversia:token` | String | 3600 s | Raw bearer token string |

### Conversational Session Memory

| Key | Type | TTL | Value |
|---|---|---|---|
| `traversia:session:{sessionId}:memory` | List (RPUSH / LRANGE) | 86400 s | JSON-encoded `ConversationalTurn` objects |

### Polling State

| Key | Type | TTL | Value |
|---|---|---|---|
| `traversia:session:{sessionId}:poll` | Hash | 86400 s | Fields: `searchKey`, `cacheKey`, `autoSuggestId`, `pollIteration`, `pollStartTime`, `destination`, `checkIn`, `checkOut` |

**Future extension**: `traversia:session:{sessionId}:embeddings` for RAG personalisation (Principle X — pre-reserved namespace).

---

## 3. Pydantic Models (AI Service — `ai-service/models/`)

### `models/search.py`

```python
from pydantic import BaseModel
from typing import List, Optional

# --- Request DTOs (mirroring Spring Boot contracts exactly) ---

class AutosuggestIdentifier(BaseModel):
    uniqueIdentifier: str
    type: str
    name: str

class RoomGuest(BaseModel):
    guestType: str  # "ADT" | "CHD"

class Room(BaseModel):
    roomNo: int
    guests: List[RoomGuest]

class AutoSuggestPayload(BaseModel):
    autoSuggestKey: str

class AutoSuggestRequest(BaseModel):
    correlationId: str
    payload: AutoSuggestPayload

class HotelSearchPayload(BaseModel):
    autoSuggestId: str
    checkIn: str            # "YYYY-MM-DD"
    checkOut: str           # "YYYY-MM-DD"
    autosuggestIdentifier: AutosuggestIdentifier
    rooms: List[Room]

class HotelSearchRequest(BaseModel):
    correlationId: str
    payload: HotelSearchPayload

class BackgroundStatusPayload(BaseModel):
    cacheKey: str
    searchKey: str
    autoSuggestId: str

class BackgroundStatusRequest(BaseModel):
    correlationId: str
    payload: BackgroundStatusPayload

# --- Response DTOs ---

class AutoSuggestEntry(BaseModel):
    uniqueId: str
    type: str
    name: str
    cityName: Optional[str] = None
    stateName: Optional[str] = None
    countryName: Optional[str] = None

class AutoSuggestResponsePayload(BaseModel):
    success: bool
    status: int
    message: str
    autoSuggestId: str
    autoSuggests: List[AutoSuggestEntry]

class AutoSuggestResponse(BaseModel):
    capability: str
    success: bool
    status: int
    message: str
    correlationId: str
    payload: AutoSuggestResponsePayload

class HotelCard(BaseModel):
    hotelId: str
    hotelName: str
    city: str
    rating: float
    price: float
    currency: str
    availableRooms: int

class HotelSearchDataPayload(BaseModel):
    hotels: List[HotelCard]
    searchKey: Optional[str] = None
    cacheKey: Optional[str] = None

class HotelSearchResponsePayload(BaseModel):
    success: bool
    message: str
    status: int
    data: HotelSearchDataPayload

class HotelSearchResponse(BaseModel):
    correlationId: str
    capability: str
    success: bool
    status: int
    message: str
    payload: HotelSearchResponsePayload

class BackgroundStatusData(BaseModel):
    status: int
    inProgress: bool
    cacheKey: str

class BackgroundStatusResponsePayload(BaseModel):
    success: bool
    status: int
    message: str
    data: BackgroundStatusData

class BackgroundStatusResponse(BaseModel):
    capability: str
    success: bool
    status: int
    message: str
    correlationId: str
    payload: BackgroundStatusResponsePayload
```

### `models/hotel.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, Any

class HotelDetailsPayload(BaseModel):
    searchKey: str
    hotelId: str

class HotelDetailsRequest(BaseModel):
    payload: HotelDetailsPayload

class HotelDetailsResponsePayload(BaseModel):
    success: bool
    status: int
    message: str
    searchKey: str
    hotelData: Any  # Full hotel object — consumed as-is per constitution

class HotelDetailsResponse(BaseModel):
    capability: str
    success: bool
    status: int
    message: str
    correlationId: str
    payload: HotelDetailsResponsePayload
```

### `models/room.py`

```python
from pydantic import BaseModel
from typing import List, Any, Optional

class RoomDetailsPayload(BaseModel):
    autoSuggestId: str
    searchKey: str
    hotelId: str
    filterBySupplier: List[str] = []  # Always [] for MVP

class RoomDetailsRequest(BaseModel):
    payload: RoomDetailsPayload

class RoomDataPayload(BaseModel):
    hotelId: str
    standardRooms: Any  # Room list — consumed as-is per constitution

class RoomDetailsResponsePayload(BaseModel):
    success: bool
    status: int
    message: str
    autoSuggestId: str
    searchKey: str
    roomData: RoomDataPayload

class RoomDetailsResponse(BaseModel):
    capability: str
    success: bool
    status: int
    message: str
    correlationId: str
    payload: RoomDetailsResponsePayload
```

### `models/errors.py`

```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"           # 400
    TOKEN_EXPIRED = "TOKEN_EXPIRED"                 # 401
    NO_RESULT = "NO_RESULT"                         # 404
    DOWNSTREAM_NULL = "DOWNSTREAM_NULL"             # 500 / 502
    DOWNSTREAM_ERROR = "DOWNSTREAM_ERROR"           # 502
    DOWNSTREAM_TIMEOUT = "DOWNSTREAM_TIMEOUT"       # 504
    INTERNAL_ERROR = "INTERNAL_ERROR"               # 500
    POLL_TIMEOUT = "POLL_TIMEOUT"                   # custom: 60 s exceeded
    TOKEN_REFRESH_FAILED = "TOKEN_REFRESH_FAILED"   # token retry also failed
    NO_AUTOSUGGEST_RESULT = "NO_AUTOSUGGEST_RESULT" # destination not found

class TraversiaError(BaseModel):
    code: ErrorCode
    message: str                  # User-safe message (no apiPath, no errorTime)
    recoverable: bool             # Whether user can retry
    capability: Optional[str] = None  # From Spring Boot "capability" field
```

### `models/token.py`

```python
from pydantic import BaseModel, Field

class TokenRequest(BaseModel):
    moduleID: str
    userName: str
    password: str

class TokenResponse(BaseModel):
    token: str
    correleationId: str  # Note: sic — double-e, matches Spring Boot exactly
    message: str
    tokenClaims: None
    tokenValid: bool
```

---

## 4. TypeScript Interfaces (Frontend — `frontend/types/`)

All interfaces mirror the Pydantic models above. Updated in the same commit as any Pydantic change (Principle V).

### `types/search.ts`

```typescript
export interface AutoSuggestEntry {
  uniqueId: string
  type: string
  name: string
  cityName?: string
  stateName?: string
  countryName?: string
}

export interface HotelCard {
  hotelId: string
  hotelName: string
  city: string
  rating: number
  price: number
  currency: string
  availableRooms: number
}

export interface SearchHistoryEntry {
  sessionId: string
  destination: string
  checkIn: string
  checkOut: string
  adultCount: number
  roomCount: number
}
```

### `types/room.ts`

```typescript
export interface RoomOption {
  // Mirrors Spring Boot standardRooms payload — consumed as-is
  [key: string]: unknown
}

export interface RoomData {
  hotelId: string
  standardRooms: RoomOption[]
}
```

### `types/sse.ts`

```typescript
export type SearchState = 'idle' | 'searching' | 'streaming' | 'complete' | 'error'

export interface SseHotelsBatchEvent {
  hotels: HotelCard[]
  batchIndex: number
}

export interface SseThinkingEvent {
  message: string
}

export interface SseSearchCompleteEvent {
  totalHotels: number
  searchKey: string
  autoSuggestId: string
}

export interface SseErrorEvent {
  code: string
  message: string
  recoverable: boolean
  capability?: string
}
```

### `types/hotel.ts`

```typescript
export interface HotelData {
  // Full hotel detail object — consumed as-is from Spring Boot
  [key: string]: unknown
}

export interface HotelDetailsResponse {
  capability: string
  success: boolean
  status: number
  message: string
  correlationId: string
  payload: {
    success: boolean
    status: number
    message: string
    searchKey: string
    hotelData: HotelData
  }
}
```

---

## 5. LangGraph State Schema

```python
# ai-service/agents/hotel_search_graph.py

from typing import TypedDict, List, Optional

class SearchState(TypedDict):
    # Identity
    session_id: str
    correlation_id: str
    query: str

    # Extracted intent
    destination: str
    destination_type: str        # "CITY" | "HOTEL" | "AREA"
    check_in: str                # "YYYY-MM-DD"
    check_out: str               # "YYYY-MM-DD"
    adult_count: int
    child_count: int
    room_count: int

    # AutoSuggest outputs
    auto_suggest_id: Optional[str]
    autosuggest_identifier: Optional[dict]
    autosuggest_candidates: Optional[list]   # For disambiguation

    # Search API outputs (lifecycle keys)
    search_key: Optional[str]
    cache_key: Optional[str]

    # Polling state
    poll_iteration: int
    poll_start_time: float       # Unix timestamp
    poll_in_progress: bool

    # Results
    hotels: List[dict]
    is_search_complete: bool

    # Error
    error: Optional[dict]        # TraversiaError serialised to dict
```

---

## 6. Entity Relationship Summary

```
search_history (MySQL)
  session_id → references Redis session (no FK — async write, sessions in Redis)
  auto_suggest_id → from AutoSuggest API
  search_key → from Search API (nullable — logged when available)

Redis session:{sessionId}:poll
  searchKey → from Search API
  cacheKey  → from Search API
  autoSuggestId → from AutoSuggest API

Redis session:{sessionId}:memory
  List of ConversationalTurn (role, content, timestamp)

Future:
  traveller (MySQL V2) → session_id FK
  booking (MySQL V3)   → session_id FK, search_key FK
```
