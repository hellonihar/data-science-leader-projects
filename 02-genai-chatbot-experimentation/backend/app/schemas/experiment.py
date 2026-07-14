import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ExperimentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    description: str = Field(default="", max_length=5000)
    traffic_split: float = Field(default=0.5, ge=0.0, le=1.0)


class ExperimentUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=5000)
    status: str | None = Field(default=None, pattern=r"^(draft|active|archived)$")
    traffic_split: float | None = Field(default=None, ge=0.0, le=1.0)


class ExperimentResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    status: str
    traffic_split: float
    model_a: str
    model_b: str
    created_at: str
    updated_at: str
