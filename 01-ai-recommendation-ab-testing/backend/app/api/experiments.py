import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.experiment import ExperimentCreate, ExperimentResponse, ExperimentUpdate
from app.services.experiment_service import ExperimentService

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


@router.get("", response_model=list[ExperimentResponse])
async def list_experiments(session: AsyncSession = Depends(get_session)):
    service = ExperimentService(session)
    return await service.list_experiments()


@router.post("", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    data: ExperimentCreate,
    session: AsyncSession = Depends(get_session),
):
    service = ExperimentService(session)
    return await service.create_experiment(
        name=data.name,
        description=data.description,
        traffic_split=data.traffic_split,
        variant_a=data.variant_a_label,
        variant_b=data.variant_b_label,
    )


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    service = ExperimentService(session)
    experiment = await service.get_experiment(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.patch("/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    experiment_id: uuid.UUID,
    data: ExperimentUpdate,
    session: AsyncSession = Depends(get_session),
):
    service = ExperimentService(session)
    experiment = await service.update_experiment(
        experiment_id,
        name=data.name,
        description=data.description,
        status=data.status,
        traffic_split=data.traffic_split,
    )
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment
