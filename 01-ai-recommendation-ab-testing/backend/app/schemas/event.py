import uuid
from datetime import datetime

from pydantic import BaseModel


class EventCreate(BaseModel):
    user_id: uuid.UUID
    item_id: uuid.UUID
    interaction_type: str
    experiment_id: uuid.UUID | None = None
    variant: str | None = None
    revenue: float | None = None
    timestamp: datetime | None = None


class EventResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    item_id: uuid.UUID
    interaction_type: str
    experiment_id: uuid.UUID | None
    variant: str | None
    revenue: float | None
    timestamp: datetime

    class Config:
        from_attributes = True
