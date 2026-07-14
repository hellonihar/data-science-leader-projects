import uuid
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: uuid.UUID
    experiment_id: uuid.UUID
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: uuid.UUID | None = None


class ChunkInfo(BaseModel):
    id: str
    content: str
    score: float


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    message_id: uuid.UUID
    variant: str
    content: str
    latency_ms: int
    retrieved_chunks: list[ChunkInfo] = []


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    variant: str | None
    latency_ms: int | None
    created_at: str
