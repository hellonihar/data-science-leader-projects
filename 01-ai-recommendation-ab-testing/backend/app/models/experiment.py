import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Experiment(TimestampMixin, Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    traffic_split: Mapped[float] = mapped_column(Float, default=0.5)
    variant_a_label: Mapped[str] = mapped_column(String(100), default="collaborative_filtering")
    variant_b_label: Mapped[str] = mapped_column(String(100), default="deep_learning")
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    interactions = relationship("Interaction", back_populates="experiment")
    assignments = relationship("Assignment", back_populates="experiment")
