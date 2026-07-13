# AI Recommendation A/B Testing Platform

Compare **collaborative filtering** vs. **deep learning** recommendations with real-time A/B testing and analytics dashboards.

## Layers Covered
Frontend, Backend, AI/ML, Analytics

## Architecture

```
frontend/  →  React + TypeScript + Recharts
backend/   →  FastAPI + SQLAlchemy + PostgreSQL
ml/        →  Collaborative Filtering (SVD) / Deep Learning (NCF)
```

## Quick Start

### 1. Start Infrastructure

```bash
docker compose up -d postgres redis
```

### 2. Run Database Migrations

```bash
cd backend
uv run alembic upgrade head
```

### 3. Seed Sample Data

```bash
cd backend
uv run python -m app.seed
```

Or do both in one step:
```bash
cd backend
.\scripts\migrate.ps1     # Windows
```

### 4. Train ML Models

```bash
cd ml
uv run python collaborative_filtering/train.py
uv run python deep_learning/train.py
```

### 5. Start Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

### 6. Start Frontend

```bash
cd frontend
npm run dev
```

### 7. Open Browser

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

### Reset Database

```bash
cd backend
.\scripts\reset_db.ps1    # Windows
```

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Users receiving recommendations |
| `items` | Products/catalog items |
| `interactions` | User events (impressions, clicks, purchases) |
| `experiments` | A/B experiment configurations |
| `assignments` | User-to-experiment-variant mappings |

## Database Scripts

| Script | Command | Description |
|--------|---------|-------------|
| Migration | `uv run alembic upgrade head` | Apply pending migrations |
| Seed | `uv run python -m app.seed` | Insert 100 users, 50 items, 1 active experiment, 1000+ interactions |
| Reset | `.\scripts\reset_db.ps1` | Drop all tables, re-migrate, re-seed |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recommendations` | Get recommendations for a user |
| POST | `/api/events` | Track user interaction |
| GET | `/api/experiments` | List all experiments |
| POST | `/api/experiments` | Create a new experiment |
| PATCH | `/api/experiments/:id` | Update experiment |
| GET | `/api/analytics/experiments/:id` | Get experiment analytics |
