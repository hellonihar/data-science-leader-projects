import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DynamicSetting(Base):
    __tablename__ = "dynamic_settings"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False, default="")
    value_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default="str"
    )
    label: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(
        String(64), nullable=False, default="general", index=True
    )
    min_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<DynamicSetting {self.key}={self.value}>"
