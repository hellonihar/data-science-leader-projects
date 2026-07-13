import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.analytics import ExperimentAnalytics
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/experiments/{experiment_id}", response_model=ExperimentAnalytics)
async def get_experiment_analytics(
    experiment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    service = AnalyticsService(session)
    result = await service.get_experiment_analytics(experiment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return result
