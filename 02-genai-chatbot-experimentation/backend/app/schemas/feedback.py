import uuid
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    message_id: uuid.UUID
    rating: int | None = Field(default=None, ge=1, le=5)
    thumbs_up: bool | None = None
