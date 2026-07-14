import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="draft", index=True
    )
    traffic_split: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    model_a: Mapped[str] = mapped_column(String(128), nullable=False, default="baseline")
    model_b: Mapped[str] = mapped_column(String(128), nullable=False, default="finetuned-rag")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Experiment {self.name} ({self.status})>"
