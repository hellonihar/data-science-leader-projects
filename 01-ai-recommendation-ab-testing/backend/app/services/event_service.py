import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interaction import Interaction


class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def track_event(
        self,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
        interaction_type: str,
        experiment_id: uuid.UUID | None = None,
        variant: str | None = None,
        revenue: float | None = None,
        timestamp: datetime | None = None,
    ) -> Interaction:
        interaction = Interaction(
            user_id=user_id,
            item_id=item_id,
            interaction_type=interaction_type,
            experiment_id=experiment_id,
            variant=variant,
            revenue=revenue,
            timestamp=timestamp or datetime.now(timezone.utc),
        )
        self.session.add(interaction)
        await self.session.commit()
        await self.session.refresh(interaction)
        return interaction
