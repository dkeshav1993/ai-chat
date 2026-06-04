# NexTrip AI — Conversational Hotel Discovery Platform

> An AI-orchestrated hotel search platform powered by **Nuxt 3**, **FastAPI**, and **LangGraph**. Type a natural-language query like "Find me a hotel in Mumbai from 20 Oct to 23 Oct for 2 adults" and watch hotel cards appear in real time via Server-Sent Events.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Nuxt 3, Vue 3 Composition API, TypeScript (strict), Tailwind CSS |
| AI Service | FastAPI, LangGraph, OpenAI SDK (GPT-4o), `sse-starlette` |
| Persistence | Redis 7 (token & session state), MySQL 8 (search history) |
| HTTP Client | `httpx` (async) |
| Migrations | Flyway |
| Infrastructure | Docker Compose |

---

## Architecture

```
Frontend (Nuxt 3 :3000)
       │
       │ SSE + REST via /api proxy
       ▼
AI Service (FastAPI :8000)
       │
       │ httpx calls
       ▼
Spring Boot Hotel APIs (thomas cook)
       ▲
       │
Redis (token cache + session state)
MySQL (search history — fire-and-forget)
```

**Key rules:**
- All Spring Boot calls go through FastAPI — frontend never calls them directly
- SSE never closes silently — always emits a structured error event
- Token lifecycle fully automated (Redis-cached, retry-once on 401)
- MySQL writes are async fire-and-forget — never on the critical path

---

## Quickstart

See [`specs/001-ai-hotel-discovery-platform/quickstart.md`](specs/001-ai-hotel-discovery-platform/quickstart.md) for the complete setup guide.

**3-command startup cheatsheet:**

```bash
# 1. Start infrastructure (MySQL + Redis + Flyway migration)
docker compose up -d

# 2. Start AI service
cd ai-service && uvicorn main:app --reload --port 8000 --log-config uvicorn_log.json

# 3. Start frontend
cd frontend && npm install && npm run dev
```

Then open [http://localhost:3000](http://localhost:3000) 🚀

---

## Environment Variables

> ⚠️ Always copy `.env.example` to `.env` and fill in your actual values before starting.

```bash
cp .env.example .env
# Edit .env — set OPENAI_API_KEY to your actual key
```

See `.env.example` for all required variables. Never commit `.env` to source control — it is gitignored.

---

## Project Structure

```
ai-chat/
├── frontend/          # Nuxt 3 frontend
├── ai-service/        # FastAPI + LangGraph AI service
├── db/migrations/     # Flyway SQL migrations
├── api/               # Spring Boot API documentation
├── specs/             # Feature specifications and plans
├── docker-compose.yml
├── .env.example       # ← Copy this to .env
└── README.md
```

---

## API Documentation

Spring Boot wrapper API docs: [`api/Hotel-Search-doc.md`](api/Hotel-Search-doc.md)

---

## Feature Specification

Full design documents: [`specs/001-ai-hotel-discovery-platform/`](specs/001-ai-hotel-discovery-platform/)

- [Plan](specs/001-ai-hotel-discovery-platform/plan.md) — architecture, lifecycle diagrams
- [Quickstart](specs/001-ai-hotel-discovery-platform/quickstart.md) — full setup guide
- [Data Model](specs/001-ai-hotel-discovery-platform/data-model.md) — entities and relationships
