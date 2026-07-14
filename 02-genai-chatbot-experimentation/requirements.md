# Project 2: GenAI Chatbot Experimentation Hub — Requirements

## 1. Overview

A full-stack A/B testing platform that compares a **baseline chatbot** (direct LLM, no context) against a **fine-tuned LLM with RAG** (Retrieval-Augmented Generation). The system tracks resolution rates, hallucination risks, user satisfaction, and Responsible AI governance metrics.

**Layers covered:** Backend, AI/ML, Analytics, Governance

---

## 2. Architecture

### 2.1 High-Level Structure

```
02-genai-chatbot-experimentation/
├── docker-compose.yml            # PostgreSQL, Redis, backend services
├── frontend/                     # React SPA
├── backend/                      # FastAPI REST API
└── evaluation/                   # Offline hallucination & fairness evaluation scripts
```

### 2.2 Tech Stack

| Layer              | Technology                              |
|--------------------|-----------------------------------------|
| Frontend           | React 19 + TypeScript 6 + Vite 8 + Recharts |
| Backend            | FastAPI + SQLAlchemy async + PostgreSQL |
| Vector Store       | pgvector (PostgreSQL extension)         |
| LLM                | Groq API (Llama 3 / Mixtral)            |
| Embeddings         | Groq API embeddings or sentence-transformers |
| Async Tasks        | Redis + ARQ or Celery                   |
| Hallucination      | Custom NLI-based factual consistency scorer |
| Containerization   | Docker Compose                          |
| Package Manager    | uv (Python), npm (frontend)             |

---

## 3. Functional Requirements

### 3.1 Chat Interface (Frontend)

| ID   | Requirement |
|------|-------------|
| F-01 | Side-by-side chat UI showing responses from both variants simultaneously |
| F-02 | Each response annotated with variant label (Baseline / Fine-tuned+RAG) |
| F-03 | Conversation history displayed in threaded format |
| F-04 | User can provide feedback per response: thumbs up/down + resolution rating (1-5) |
| F-05 | User can start a new conversation at any time |
| F-06 | Loading indicators during response generation |
| F-07 | Latency shown per response (time to first token, total time) |

### 3.2 Experiment Management (Backend)

| ID   | Requirement |
|------|-------------|
| F-08 | Create A/B experiments with name, description, traffic split percentage |
| F-09 | Start / stop / archive experiments |
| F-10 | Users deterministically assigned to variants via SHA-256 hash of `user_id:experiment_id:salt` |
| F-11 | Variant A = baseline (direct LLM, no retrieval) |
| F-12 | Variant B = fine-tuned LLM with RAG context |

### 3.3 RAG Pipeline (Backend)

| ID   | Requirement |
|------|-------------|
| F-13 | Document ingestion: upload text/PDF/markdown files |
| F-14 | Document chunking with configurable chunk size and overlap |
| F-15 | Embedding generation and storage in pgvector |
| F-16 | Semantic retrieval: top-k chunks retrieved per user query |
| F-17 | Retrieved context injected into prompt for Variant B |
| F-18 | Document management: list, view, delete indexed documents |

### 3.4 Baseline LLM (Backend)

| ID   | Requirement |
|------|-------------|
| F-19 | Direct LLM call with only the user query and a system prompt |
| F-20 | No external context or retrieved documents provided |
| F-21 | Same base model as Variant B (to isolate RAG/fine-tuning effect) |

### 3.5 Fine-tuned LLM + RAG (Backend)

| ID   | Requirement |
|------|-------------|
| F-22 | Fine-tuned version of the base model (deployed separately) |
| F-23 | RAG pipeline injects top-k retrieved document chunks into the prompt |
| F-24 | Retrieved context displayed alongside the response (for transparency) |

### 3.6 Hallucination Detection (Backend / Evaluation)

| ID   | Requirement |
|------|-------------|
| F-25 | Automated hallucination scoring per response on Variant B |
| F-26 | Factual consistency check: compare response claims against retrieved documents |
| F-27 | Score categories: Consistent, Minor Inconsistency, Major Hallucination |
| F-28 | Hallucination scores stored and aggregated for analytics |

### 3.7 Analytics Dashboard (Frontend + Backend)

| ID   | Requirement |
|------|-------------|
| F-29 | Real-time comparison dashboard: Baseline vs. Fine-tuned+RAG |
| F-30 | Key metrics: resolution rate, avg hallucination score, avg latency, token cost |
| F-31 | Time-series charts showing metric trends |
| F-32 | Bar charts comparing variants head-to-head |
| F-33 | Statistical significance testing (chi-square for resolution rate, t-test for latency) |

### 3.8 Responsible AI Governance (Frontend + Backend)

| ID   | Requirement |
|------|-------------|
| F-34 | Fairness metrics: response quality across query categories/topics |
| F-35 | Transparency logs: which variant served, which documents retrieved, which model used |
| F-36 | Audit trail: all experiment changes, user assignments, model versions |
| F-37 | Bias detection: flag if response quality differs significantly across topic categories |

---

## 4. Non-Functional Requirements

| ID   | Requirement |
|------|-------------|
| N-01 | All API responses < 500ms (excluding LLM generation time) |
| N-02 | Concurrent user support via async FastAPI + asyncpg |
| N-03 | LLM calls should timeout after 60s with graceful fallback |
| N-04 | All LLM responses logged for audit and evaluation |
| N-05 | PII not stored in conversation logs (configurable redaction) |
| N-06 | Docker Compose one-command startup for local development |
| N-07 | Alembic migrations for database schema versioning |
| N-08 | Seed scripts for demo data (sample documents, sample conversations) |

---

## 5. Database Schema

### Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `users` | Chat users | id (UUID), username, created_at |
| `conversations` | Chat sessions | id (UUID), user_id (FK), title, experiment_id (FK), created_at |
| `messages` | Individual messages | id (UUID), conversation_id (FK), role (user/assistant), content, variant (A/B), latency_ms, token_count, created_at |
| `experiments` | A/B test configurations | id (UUID), name, description, status, traffic_split, model_a, model_b, created_at |
| `assignments` | User-to-variant mapping | id (UUID), user_id (FK), experiment_id (FK), variant (A/B), assigned_at |
| `feedback` | User ratings | id (UUID), message_id (FK), rating (1-5), thumbs_up (bool), created_at |
| `hallucination_scores` | Automated evaluation | id (UUID), message_id (FK), score (0-1), category, details_json, created_at |
| `documents` | RAG-indexed content | id (UUID), filename, chunk_index, content, embedding (vector), metadata_json, created_at |
| `audit_log` | Governance audit trail | id (UUID), action, entity_type, entity_id, details_json, created_at |

---

## 6. API Endpoints

### 6.1 Chat

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Send a message (variant auto-assigned per experiment) |
| GET | `/api/conversations` | List user's conversations |
| GET | `/api/conversations/{id}` | Get full conversation with messages |
| DELETE | `/api/conversations/{id}` | Delete a conversation |

### 6.2 Feedback

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/feedback` | Submit thumbs up/down + rating for a message |

### 6.3 Experiments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/experiments` | List all experiments |
| POST | `/api/experiments` | Create a new experiment |
| GET | `/api/experiments/{id}` | Get experiment details |
| PATCH | `/api/experiments/{id}` | Update experiment (status, traffic split) |

### 6.4 Documents (RAG Management)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/documents/upload` | Upload a document for indexing |
| GET | `/api/documents` | List all indexed documents |
| DELETE | `/api/documents/{id}` | Delete a document and its chunks |

### 6.5 Analytics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/analytics/experiments/{id}` | Aggregate metrics for an experiment |
| GET | `/api/analytics/hallucination` | Hallucination score distribution |
| GET | `/api/analytics/latency` | Latency comparison across variants |

### 6.6 Governance

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/governance/fairness` | Fairness metrics by topic category |
| GET | `/api/governance/audit` | Audit trail log |
| GET | `/api/governance/transparency/{message_id}` | Full transparency details for a response |

---

## 7. Frontend Routes

| Route | Page | Description |
|-------|------|-------------|
| `/` | Chat | Main side-by-side chat interface |
| `/experiments` | Experiments | CRUD for A/B experiments |
| `/dashboard` | Dashboard | Analytics charts and metrics |
| `/governance` | Governance | Fairness, audit, transparency dashboard |
| `/documents` | Documents | RAG document management |

---

## 8. Evaluation & Metrics

### 8.1 Primary Metrics

| Metric | Description |
|--------|-------------|
| Resolution Rate | % of conversations where user marks issue as resolved (rating >= 4) |
| Hallucination Score | Average factual consistency score per variant |
| User Satisfaction | Average feedback rating (1-5) |
| Latency P95 | 95th percentile response time |
| Token Cost | Average tokens per response |

### 8.2 Responsible AI Metrics

| Metric | Description |
|--------|-------------|
| Fairness Gap | Variance in resolution rate across topic categories |
| Transparency Score | % of responses with complete provenance data |
| Audit Coverage | % of experiment changes with logged audit trail |

---

## 9. Out of Scope (Future Phases)

| Item | Rationale |
|------|-----------|
| Multi-LLM provider comparison | Single provider (Groq API) for controlled experiment |
| Streaming responses | SSE adds complexity; batch responses for MVP |
| User authentication / SSO | Simple user ID header for MVP; auth in later phase |
| Production-grade content filtering | Basic filtering only; advanced RAI filtering deferred |
