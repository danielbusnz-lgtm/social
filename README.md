# HiveNet

A full-stack social network with timelines, follows, and likes. Built to practice production patterns end to end: async Python on the backend, the modern Next.js stack on the frontend, and Playwright for E2E confidence.

**Live demo:** https://hivenet-three.vercel.app

## Features

- Email + password registration with hashed credentials
- JWT-authenticated sessions with route-level guards on the client
- Compose posts, view a personal timeline of accounts you follow
- Follow and unfollow other users
- Like and unlike posts with optimistic UI and idempotent backend toggles
- Profile page with post history and account metadata
- UTC-normalized timestamps with relative "time ago" formatting

## Tech stack

**Backend** — FastAPI · SQLAlchemy 2.0 (async) · asyncpg · Pydantic · python-jose · bcrypt · uvicorn · pytest

**Frontend** — Next.js 16 · React 19 · TypeScript · Tailwind CSS 4 · Headless UI

**Infra** — PostgreSQL · Vercel (frontend) · Docker (backend)

**Testing** — Playwright (E2E) · pytest (backend unit)

## Architecture

```
Next.js (Vercel)  ──▶  FastAPI (Docker)  ──▶  PostgreSQL
                       └─ JWT auth
                       └─ async SQLAlchemy
                       └─ Pydantic schemas
```

The frontend is a client-rendered Next.js app that talks to the FastAPI backend over an `API_URL` env variable. JWTs are stored in `localStorage` and sent on every request via an `Authorization: Bearer` header. An `AuthGate` client component redirects unauthenticated users to `/login`.

The backend is fully async — all DB access uses SQLAlchemy's async session and asyncpg. Schema is defined as `DeclarativeBase` models with FK relations and unique constraints. Tables are created on startup via the FastAPI `lifespan` hook.

## API surface

| Method | Path | Description |
|---|---|---|
| `POST` | `/register` | Create an account |
| `POST` | `/login` | Exchange credentials for a JWT |
| `GET` | `/me` | Current user profile + post count |
| `GET` | `/me/posts` | Authored posts |
| `POST` | `/posts` | Create a post |
| `GET` | `/feed` | Posts from accounts you follow plus your own |
| `POST` | `/posts/{id}/like` | Like a post (idempotent) |
| `DELETE` | `/posts/{id}/like` | Unlike a post |
| `POST` | `/follow/{user_id}` | Follow another user |

Interactive OpenAPI docs are exposed at `/docs` when the backend is running.

## Local development

### Prerequisites

- Python 3.12+ with [`uv`](https://docs.astral.sh/uv/)
- Node.js 20+
- PostgreSQL 14+ running locally

### Backend

```bash
cd backend
createdb social
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

The app reads `DATABASE_URL` and `JWT_SECRET` from the environment. Sensible defaults are provided for local development; override them in production.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend reads `NEXT_PUBLIC_API_URL` and falls back to `http://localhost:8000`.

Open http://localhost:3000.

## Testing

### End-to-end

```bash
cd frontend
npx playwright install chromium
npx playwright test
```

Playwright auto-spawns both the backend and frontend dev servers via the `webServer` config. The bundled spec covers a full user journey: register → log in → post → like → unlike, with assertions on the like count and `aria-pressed` state.

### Backend

```bash
cd backend
uv run pytest
```

## Project layout

```
backend/
  app/
    main.py           FastAPI app + lifespan + CORS
    auth.py           JWT + password hashing
    database.py       Async engine + session
    models.py         SQLAlchemy models
    schemas.py        Pydantic request/response models
    routes/           Route handlers (users, posts, follows)
  tests/              pytest suite

frontend/
  src/
    app/              Next.js App Router pages
    components/       Shared UI components and feature widgets
    lib/api.ts        API base URL
  e2e/                Playwright specs
```

## License

MIT — see [LICENSE](./LICENSE).
