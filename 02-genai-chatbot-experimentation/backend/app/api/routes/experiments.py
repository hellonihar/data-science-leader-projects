import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.experiment import Experiment
from app.schemas.experiment import ExperimentCreate, ExperimentUpdate, ExperimentResponse

router = APIRouter()


def _to_response(e: Experiment) -> ExperimentResponse:
    return ExperimentResponse(
        id=e.id,
        name=e.name,
        description=e.description,
        status=e.status,
        traffic_split=e.traffic_split,
        model_a=e.model_a,
        model_b=e.model_b,
        created_at=e.created_at.isoformat(),
        updated_at=e.updated_at.isoformat(),
    )


@router.get("", response_model=list[ExperimentResponse])
async def list_experiments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Experiment).order_by(Experiment.created_at.desc())
    )
    return [_to_response(e) for e in result.scalars().all()]


@router.post("", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    req: ExperimentCreate,
    db: AsyncSession = Depends(get_db),
):
    experiment = Experiment(
        name=req.name,
        description=req.description,
        traffic_split=req.traffic_split,
    )
    db.add(experiment)
    await db.flush()
    await db.refresh(experiment)
    return _to_response(experiment)


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    experiment = await db.get(Experiment, experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return _to_response(experiment)


@router.patch("/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    experiment_id: uuid.UUID,
    req: ExperimentUpdate,
    db: AsyncSession = Depends(get_db),
):
    experiment = await db.get(Experiment, experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    update_data = req.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(Experiment)
            .where(Experiment.id == experiment_id)
            .values(**update_data)
        )
        await db.flush()
        await db.refresh(experiment)

    return _to_response(experiment)
