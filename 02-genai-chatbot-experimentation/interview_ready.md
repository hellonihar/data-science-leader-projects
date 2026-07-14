# GenAI Chatbot Experimentation Hub — Systematic Implementation Plan

## Problem Domain & Solution Approach

Enterprises deploying generative AI chatbots face a critical challenge: how do you rigorously measure whether your chatbot is actually improving outcomes? Without A/B testing, teams rely on intuition and anecdotal feedback, leading to deployment of models that may hallucinate more, frustrate users, or serve answers inconsistently across topics. The core problem is that LLM-based chatbots are stochastic systems — the same prompt can produce meaningfully different responses, making it difficult to isolate whether a change to the model, prompt, or retrieval strategy actually drives better user outcomes. Organizations need a repeatable, data-driven experimentation framework that treats the chatbot as a product feature to be optimized, not just an API endpoint to be integrated.

This project addresses that gap by building a full-stack A/B testing platform purpose-built for GenAI chatbots. The system compares two variants head-to-head: a Baseline variant that sends user queries directly to a large language model with no additional context, and a Fine-tuned + RAG variant that first retrieves relevant document chunks from a vector database and injects them into the prompt before generation. By serving both variants simultaneously to deterministically assigned users, the platform isolates the marginal impact of retrieval-augmented generation on response quality, latency, and cost. The entire system is designed to produce statistically defensible answers to questions like "Does adding RAG improve resolution rate?" and "Does the fine-tuned model hallucinate less?"

The solution approach follows a layered architecture. At the infrastructure layer, Docker Compose orchestrates PostgreSQL with pgvector for unified relational storage and vector embeddings, Redis for caching and async task queues, and a FastAPI backend that handles all API traffic asynchronously. The backend implements a deterministic user assignment engine using SHA-256 hashing to ensure consistent variant exposure without session drift, a pluggable LLM router that dispatches to either the baseline or fine-tuned model with latency instrumentation, and a complete RAG pipeline with document chunking, embedding, and semantic retrieval. Every response is automatically scored for factual consistency using a custom NLI-based hallucination detector that compares generated claims against the retrieved source documents.

On the analytics and governance front, the platform computes real-time aggregate metrics — resolution rate, hallucination score, P95 latency, and token cost — grouped by variant with automatic statistical significance testing (chi-square for proportions, t-test for continuous metrics). A governance layer tracks fairness gaps across topic categories, maintains a full audit trail of all experiment changes and model assignments, and provides transparency endpoints that expose exactly which documents and model version produced each response. This ensures the platform not only measures performance but also supports Responsible AI requirements around bias detection, reproducibility, and compliance.

The frontend is a React 19 SPA with a side-by-side chat interface that displays both variants simultaneously for direct comparison, a feedback widget for collecting user satisfaction ratings, and three dashboard views: an analytics dashboard with Recharts time-series and bar charts, an experiment management interface for controlling A/B tests, and a governance dashboard with fairness heatmaps, audit logs, and transparency panels. The result is a complete, containerized experimentation platform that enables data science and product teams to make evidence-based decisions about their GenAI chatbot investments — from model selection and prompt engineering to RAG strategy and fine-tuning methodology.

## Data & Information Flow by Variant

### Variant A — Baseline (Direct LLM, No Retrieval)

```text
User Query ──► POST /api/chat ──► Assignment Lookup (Redis/DB)
                                         │
                                    Variant A
                                         │
                                         ▼
                              Build Prompt (System + Query)
                                         │
                                         ▼
                              Groq API (Llama 3 / Mixtral)
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │  Measure: latency_ms          │
                         │  Measure: token_count         │
                         │  Log to: messages table       │
                         └──────────────────────────────┘
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │  Hallucination Scorer (NLI)   │
                         │  Score: consistent / minor /  │
                         │         major hallucination   │
                         │  Log to: hallucination_scores │
                         └──────────────────────────────┘
                                         │
                                         ▼
                         Response + metadata returned
                         to frontend side-by-side pane
```

**Data collected:** `messages` (user query, assistant response, latency_ms, token_count), `hallucination_scores` (score, category, details_json), `feedback` (rating, thumbs_up/down) — submitted asynchronously by the user after reading the response.

### Variant B — Fine-tuned LLM + RAG

```text
User Query ──► POST /api/chat ──► Assignment Lookup (Redis/DB)
                                         │
                                    Variant B
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │  Embed user query             │
                         │  (sentence-transformers or    │
                         │   Groq embeddings API)        │
                         └──────────────────────────────┘
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │  pgvector semantic search     │
                         │  cosine similarity top-k      │
                         │  Retrieve chunks with score   │
                         │  Log: retrieved doc IDs +     │
                         │        similarity scores      │
                         └──────────────────────────────┘
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │  Inject chunks into prompt    │
                         │  Template: System + Context   │
                         │  + User Query                 │
                         └──────────────────────────────┘
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │  Fine-tuned Groq API call     │
                         │  (same base model family,     │
                         │   fine-tuned on domain data)  │
                         └──────────────────────────────┘
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │  Measure: latency_ms          │
                         │  Measure: token_count         │
                         │  Log to: messages table       │
                         │  Log: retrieved chunks in     │
                         │       transparency log        │
                         └──────────────────────────────┘
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │  Hallucination Scorer (NLI)   │
                         │  Compare claims vs. retrieved │
                         │  document chunks (not just    │
                         │  model internal knowledge)    │
                         │  Log to: hallucination_scores │
                         └──────────────────────────────┘
                                         │
                                         ▼
                         Response + metadata + source
                         chunks returned to frontend
                         side-by-side pane
```

**Additional data collected (Variant B only):** `documents` table (chunks used), similarity scores per chunk, transparency payload (exact passages injected into prompt), hallucination score grounded against source documents rather than world knowledge.

### Cross-Cutting Data Flows (Both Variants)

| Flow | Data Captured | Destination |
|------|---------------|-------------|
| **User assignment** | user_id, experiment_id, variant, timestamp | `assignments` table + Redis cache |
| **Conversation threading** | conversation_id, message order, parent_message_id | `conversations` + `messages` tables |
| **User feedback** | message_id, rating (1-5), thumbs_up (bool), timestamp | `feedback` table |
| **Audit trail** | action, entity_type, entity_id, details_json, timestamp | `audit_log` table |
| **Analytics aggregation** | Resolution rate, hallucination score, P95 latency, token cost, grouped by variant + time window | Computed query → cached in Redis → served via `/api/analytics/experiments/{id}` |
| **Fairness tracking** | Resolution rate per topic category, variance across categories | `/api/governance/fairness` endpoint |
| **Statistical testing** | Chi-square p-value (resolution rate), t-test p-value (latency/hallucination) | Computed on request via analytics endpoint |

## Phase 1: Foundation & Scaffolding

1. **Initialize the project structure** — Set up the monorepo layout (`backend/`, `frontend/`, `evaluation/`) with `uv` for Python, `npm` for React 19 + Vite 8 + TypeScript 6, and `docker-compose.yml` pulling PostgreSQL with pgvector, Redis, and the backend service.

2. **Database schema & migrations** — Define all 9 tables (`users`, `experiments`, `assignments`, `conversations`, `messages`, `feedback`, `hallucination_scores`, `documents`, `audit_log`) using SQLAlchemy 2.0 async models. Enable pgvector extension. Run Alembic migrations.

3. **Base FastAPI app** — Stand up the FastAPI project with async SQLAlchemy session management, CORS, request logging, error handlers, and health check. Verify Docker Compose boots cleanly.

## Phase 2: Core Chat Pipeline

4. **Experiment management API** — Implement CRUD for experiments, including status transitions (draft → active → archived). Traffic split stored as a float 0–1.

5. **Deterministic user assignment** — SHA-256 hash of `user_id:experiment_id:salt` to assign users to Variant A (Baseline) or Variant B (Fine-tuned + RAG). Store assignment in `assignments` table; cache in Redis to avoid re-hashing on every request.

6. **Baseline variant (A)** — Route user query + system prompt directly to the Groq API (Llama 3 / Mixtral). Return response, measure latency, log token count.

7. **RAG pipeline (Variant B)** — Document ingestion: accept text/PDF/markdown uploads, chunk with configurable size/overlap, generate embeddings via Groq embeddings or sentence-transformers, store in pgvector. At query time, retrieve top-k chunks by cosine similarity, inject them into the prompt, then call the fine-tuned model.

8. **Chat API** — `POST /api/chat` accepts `user_id`, `experiment_id`, `message`. Looks up assignment, dispatches to appropriate variant, stores the message pair (user + assistant) in `conversations`/`messages`, returns both responses side-by-side with latency and token metadata.

## Phase 3: Hallucination Detection & Feedback

9. **Hallucination scorer** — Build an NLI-based factual consistency module: for each Variant B response, decompose it into atomic claims, check each claim against the retrieved document context using a natural language inference model, and score the response as *Consistent*, *Minor Inconsistency*, or *Major Hallucination*. Store in `hallucination_scores`.

10. **Feedback API** — `POST /api/feedback` captures thumbs up/down + 1–5 resolution rating per message. Link to `message_id` for traceability.

## Phase 4: Analytics & Governance

11. **Analytics aggregation** — Build SQL queries to compute: resolution rate (rating ≥ 4), average hallucination score, P95 latency, average token cost, grouped by variant and time window. Expose via `/api/analytics/experiments/{id}`. Use Redis to cache frequent aggregations.

12. **Statistical significance** — Implement chi-square test for categorical metrics (resolution rate) and independent t-test for continuous metrics (latency, hallucination score). Compute p-values and display significance labels.

13. **Governance layer** — Fairness metrics: group responses by topic category (auto-classified or user-tagged), compare resolution rate variance. Transparency endpoint: return full provenance (variant, model version, retrieved chunks). Audit trail: log every experiment CRUD, assignment, and feedback event to `audit_log`.

## Phase 5: Frontend

14. **Side-by-side chat UI** — React 19 SPA with two chat panes: left shows Baseline response, right shows Fine-tuned + RAG response. Each pane labels the variant, displays latency, and has thumbs up/down + rating widget. Threaded conversation view.

15. **Experiment management UI** — Form to create/edit experiments with traffic split slider. List of experiments with status badges, start/stop/archive actions.

16. **Analytics dashboard** — Recharts time-series charts for metric trends, bar charts for variant comparison, statistical significance badges. Latency distribution histogram.

17. **Governance dashboard** — Fairness heatmap by topic category, audit trail table with search/filter, transparency detail panel.

18. **Document management UI** — Upload panel (drag-and-drop), indexed document list with chunk counts, delete button.

## Phase 6: Integration & Polish

19. **Seed data & demo script** — Pre-populate sample documents (e.g., product FAQs, policy PDFs), sample conversations, and a pre-configured experiment so the demo is one-click.

20. **Docker Compose orchestration** — Wire all services together with proper health checks, volume mounts for persistence, and environment variable injection for API keys.

21. **End-to-end smoke test** — Spin up the stack, create an experiment, upload a document, send a chat message, verify both variants respond, submit feedback, check analytics numbers, confirm audit log entry.

---

## Key Design Decisions (for interview discussion)

| Decision | Rationale |
|----------|-----------|
| **Groq as single LLM provider** | Removes confounding variables; fast inference enables real-time experimentation |
| **pgvector instead of separate vector DB** | Reduces ops complexity; single PostgreSQL handles relational data + embeddings; ACID for audit compliance |
| **SHA-256 deterministic assignment** | Ensures consistent user experience per experiment while maintaining statistical validity |
| **Custom NLI hallucination scorer** | Offline, no third-party data leakage, fully auditable, zero marginal cost per inference |
