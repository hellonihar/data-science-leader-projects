import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.event import EventCreate, EventResponse
from app.services.event_service import EventService

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=201)
async def track_event(
    data: EventCreate,
    session: AsyncSession = Depends(get_session),
):
    service = EventService(session)
    return await service.track_event(
        user_id=data.user_id,
        item_id=data.item_id,
        interaction_type=data.interaction_type,
        experiment_id=data.experiment_id,
        variant=data.variant,
        revenue=data.revenue,
        timestamp=data.timestamp,
    )
