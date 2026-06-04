# SSE Event Contracts

**Layer**: Frontend ↔ FastAPI AI Service
**Date**: 2026-05-23
**Transport**: Server-Sent Events (`text/event-stream`)
**Endpoint**: `GET /chat/search?sessionId=...&query=...`

---

## Protocol

The frontend opens a native `EventSource` connection to the `/chat/search` endpoint. The AI service streams typed named events as the LangGraph graph progresses through each node.

The stream MUST always terminate with either a `search_complete` event or an `error` event. Silent stream closure is prohibited (Principle VII).

---

## Event Definitions

### `thinking`

Emitted when the AI is performing an intermediate step (intent extraction, AutoSuggest call, disambiguation). Provides a human-readable status message to show in the chat UI.

```
event: thinking
data: {"message": "Finding hotels in New Delhi..."}
```

**Data schema**:
```typescript
interface SseThinkingEvent {
  message: string
}
```

**When emitted**:
- After intent extraction begins
- When AutoSuggest is called
- When disambiguation options are being generated
- When Search API is called

---

### `hotels_batch`

Emitted for each batch of hotel results returned from the Search By Poll API. Multiple `hotels_batch` events are emitted during a single search — one per poll iteration that yields new hotels. The frontend appends each batch to the displayed list progressively.

```
event: hotels_batch
data: {"hotels": [{"hotelId": "H1001", "hotelName": "Sample Hotel Delhi", "city": "New Delhi", "rating": 4.2, "price": 5200, "currency": "INR", "availableRooms": 5}], "batchIndex": 0}
```

**Data schema**:
```typescript
interface SseHotelsBatchEvent {
  hotels: HotelCard[]
  batchIndex: number
}

interface HotelCard {
  hotelId: string
  hotelName: string
  city: string
  rating: number
  price: number
  currency: string
  availableRooms: number
}
```

**Frontend handling**:
```typescript
eventSource.addEventListener('hotels_batch', (e) => {
  const batch: SseHotelsBatchEvent = JSON.parse(e.data)
  hotels.value.push(...batch.hotels)
  searchState.value = 'streaming'
})
```

---

### `search_complete`

Emitted once when the poll loop has finished (either `inProgress === false` from Background Status, or the 60 s timeout was reached with partial results). After this event, the `EventSource` connection is closed by the frontend.

```
event: search_complete
data: {"totalHotels": 23, "searchKey": "8c3f42bd-401d-48cb-8cff-9ef7d22ac2e0", "autoSuggestId": "1f54982b-36b4-4e84-ac01-dc2cf102db30"}
```

**Data schema**:
```typescript
interface SseSearchCompleteEvent {
  totalHotels: number
  searchKey: string
  autoSuggestId: string
}
```

**Note**: `searchKey` and `autoSuggestId` are included in this event so the frontend can pass them to hotel detail and room detail requests without requiring a separate session state lookup. This also preserves the lifecycle keys for future fare-recheck capability (Principle X).

**Frontend handling**:
```typescript
eventSource.addEventListener('search_complete', (e) => {
  const result: SseSearchCompleteEvent = JSON.parse(e.data)
  searchState.value = 'complete'
  // Store searchKey + autoSuggestId for hotel/room detail navigation
  eventSource.close()
})
```

---

### `error`

Emitted when the search flow encounters an unrecoverable error at any stage. This is ALWAYS the last event on the stream before closure. The stream MUST NOT close without emitting this event on failure.

```
event: error
data: {"code": "POLL_TIMEOUT", "message": "Search is taking longer than expected. Showing available results.", "recoverable": true}
```

**Data schema**:
```typescript
interface SseErrorEvent {
  code: SseErrorCode
  message: string        // User-safe message — no apiPath, no errorTime, no internal details
  recoverable: boolean   // If true, user can retry; if false, session is broken
  capability?: string    // Optional — from Spring Boot capability field if applicable
}

type SseErrorCode =
  | 'NO_AUTOSUGGEST_RESULT'
  | 'VALIDATION_ERROR'
  | 'NO_RESULT'
  | 'DOWNSTREAM_NULL'
  | 'DOWNSTREAM_ERROR'
  | 'DOWNSTREAM_TIMEOUT'
  | 'POLL_TIMEOUT'
  | 'TOKEN_REFRESH_FAILED'
  | 'INTERNAL_ERROR'
```

**Frontend handling**:
```typescript
eventSource.addEventListener('error', (e) => {
  const err: SseErrorEvent = JSON.parse(e.data)
  searchError.value = err
  searchState.value = 'error'
  // Hotels already accumulated remain displayed (partial results preserved)
  eventSource.close()
})
```

**Note**: The native `EventSource` also fires an `onerror` callback on network-level failures (connection dropped). This must be handled separately from the named `error` event above:
```typescript
eventSource.onerror = () => {
  if (searchState.value !== 'complete' && searchState.value !== 'error') {
    searchError.value = { code: 'INTERNAL_ERROR', message: 'Connection lost. Please try again.', recoverable: true }
    searchState.value = 'error'
    eventSource.close()
  }
}
```

---

## Full Event Sequence Example

```
event: thinking
data: {"message": "Understanding your request..."}

event: thinking
data: {"message": "Finding hotels in New Delhi..."}

event: thinking
data: {"message": "Starting hotel search..."}

event: hotels_batch
data: {"hotels": [{"hotelId": "H1001", ...}, {"hotelId": "H1002", ...}], "batchIndex": 0}

event: hotels_batch
data: {"hotels": [{"hotelId": "H1003", ...}], "batchIndex": 1}

event: search_complete
data: {"totalHotels": 3, "searchKey": "8c3f42bd-...", "autoSuggestId": "1f54982b-..."}
```

---

## Error Sequence Example (Poll Timeout with Partial Results)

```
event: thinking
data: {"message": "Finding hotels in New Delhi..."}

event: hotels_batch
data: {"hotels": [{"hotelId": "H1001", ...}], "batchIndex": 0}

event: error
data: {"code": "POLL_TIMEOUT", "message": "Search is taking longer than expected. Showing available results.", "recoverable": true}
```

---

## Frontend State Machine

```
idle
  └─ user submits query
       ↓
searching (EventSource opened, no hotels yet)
  └─ first hotels_batch received
       ↓
streaming (hotels accumulating progressively)
  └─ search_complete received
       ↓
complete (all hotels shown, EventSource closed)

Any state + error event received
  ↓
error (partial hotels preserved, error message shown, EventSource closed)
```
