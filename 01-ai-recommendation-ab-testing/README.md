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

### 2. Train ML Models

```bash
cd ml
uv run python collaborative_filtering/train.py
uv run python deep_learning/train.py
```

### 3. Start Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

### 4. Start Frontend

```bash
cd frontend
npm run dev
```

### 5. Open Browser

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recommendations` | Get recommendations for a user |
| POST | `/api/events` | Track user interaction |
| GET | `/api/experiments` | List all experiments |
| POST | `/api/experiments` | Create a new experiment |
| PATCH | `/api/experiments/:id` | Update experiment |
| GET | `/api/analytics/experiments/:id` | Get experiment analytics |
