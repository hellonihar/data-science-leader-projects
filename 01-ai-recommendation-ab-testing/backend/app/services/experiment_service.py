import hashlib
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment
from app.models.experiment import Experiment


class ExperimentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_experiment(self, experiment_id: uuid.UUID) -> Experiment | None:
        result = await self.session.execute(
            select(Experiment).where(Experiment.id == experiment_id)
        )
        return result.scalar_one_or_none()

    async def get_active_experiment(self) -> Experiment | None:
        result = await self.session.execute(
            select(Experiment).where(Experiment.status == "active").limit(1)
        )
        return result.scalar_one_or_none()

    async def assign_user(self, user_id: uuid.UUID, experiment_id: uuid.UUID) -> str:
        result = await self.session.execute(
            select(Assignment).where(
                Assignment.user_id == user_id,
                Assignment.experiment_id == experiment_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing.variant

        key = f"{user_id}:{experiment_id}:recommendation-ab"
        hash_val = hashlib.sha256(key.encode()).hexdigest()
        variant = "A" if int(hash_val, 16) % 100 < 50 else "B"

        assignment = Assignment(
            user_id=user_id,
            experiment_id=experiment_id,
            variant=variant,
        )
        self.session.add(assignment)
        await self.session.commit()
        return variant

    async def create_experiment(self, name: str, description: str | None = None,
                                traffic_split: float = 0.5,
                                variant_a: str = "collaborative_filtering",
                                variant_b: str = "deep_learning") -> Experiment:
        experiment = Experiment(
            name=name,
            description=description,
            status="draft",
            traffic_split=traffic_split,
            variant_a_label=variant_a,
            variant_b_label=variant_b,
        )
        self.session.add(experiment)
        await self.session.commit()
        await self.session.refresh(experiment)
        return experiment

    async def update_experiment(self, experiment_id: uuid.UUID, **kwargs) -> Experiment | None:
        experiment = await self.get_experiment(experiment_id)
        if not experiment:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(experiment, key, value)
        await self.session.commit()
        await self.session.refresh(experiment)
        return experiment

    async def list_experiments(self) -> list[Experiment]:
        result = await self.session.execute(
            select(Experiment).order_by(Experiment.created_at.desc())
        )
        return list(result.scalars().all())
