import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics, events, experiments, recommendations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Recommendation A/B Testing Platform...")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="AI Recommendation A/B Testing Platform",
    description="Compare collaborative filtering vs. deep learning recommendations",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations.router)
app.include_router(experiments.router)
app.include_router(events.router)
app.include_router(analytics.router)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "recommendation-ab-testing"}
