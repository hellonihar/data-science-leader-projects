import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/experiments/{experiment_id}")
async def get_experiment_analytics(
    experiment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_experiment_metrics(experiment_id)


@router.get("/hallucination")
async def get_hallucination_distribution(
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_hallucination_distribution()


@router.get("/latency")
async def get_latency_comparison(
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_latency_comparison()
