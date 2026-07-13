import uuid
from datetime import datetime

from pydantic import BaseModel


class ExperimentCreate(BaseModel):
    name: str
    description: str | None = None
    traffic_split: float = 0.5
    variant_a_label: str = "collaborative_filtering"
    variant_b_label: str = "deep_learning"


class ExperimentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    traffic_split: float | None = None


class ExperimentResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    status: str
    traffic_split: float
    variant_a_label: str
    variant_b_label: str
    start_date: datetime | None
    end_date: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
