import uuid
from datetime import datetime

from pydantic import BaseModel


class VariantMetrics(BaseModel):
    variant: str
    total_users: int
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_revenue: float
    ctr: float
    conversion_rate: float
    revenue_per_user: float


class ExperimentAnalytics(BaseModel):
    experiment_id: uuid.UUID
    experiment_name: str
    status: str
    variants: list[VariantMetrics]
    winner: str | None
    p_value: float | None
    significant: bool | None
    revenue_lift: float | None
    ctr_lift: float | None
    updated_at: datetime | None

    class Config:
        from_attributes = True
