import uuid
from datetime import datetime

from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    user_id: uuid.UUID
    top_k: int = 10


class RecommendationItem(BaseModel):
    item_id: uuid.UUID
    name: str
    category: str
    price: float
    score: float


class RecommendationResponse(BaseModel):
    user_id: uuid.UUID
    variant: str
    experiment_id: uuid.UUID | None = None
    recommendations: list[RecommendationItem]
    model: str
