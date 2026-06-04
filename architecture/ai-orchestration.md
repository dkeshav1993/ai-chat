# AI Orchestration Architecture

The AI layer orchestrates APIs only.

The AI layer must NEVER:

* execute business logic
* directly access DB
* calculate pricing
* process payments

Existing Spring Boot APIs remain source of truth.

---

## Responsibilities of AI Layer

* conversational understanding
* extracting search intent
* orchestrating API sequence
* managing polling lifecycle
* summarizing hotels
* maintaining conversational state
* streaming updates to frontend

---

## Technology Stack

* FastAPI
* LangGraph
* OpenAI SDK
* SSE Streaming
* Redis conversational memory

---

## Polling Flow

Search API
↓
Background Process Status
↓
Search By Poll
↓
Progressive UI rendering

---

## Error Handling

Handle:

* token expiry
* validation errors
* downstream failures
* timeout failures
* empty results
* polling interruptions

---

## Future Scope

Architecture must support:

* fare recheck
* traveller forms
* booking flow
* PG orchestration
* vouchers
* personalization
* RAG
