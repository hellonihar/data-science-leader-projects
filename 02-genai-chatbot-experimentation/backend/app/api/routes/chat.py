import uuid
import json
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.models.assignment import Assignment
from app.models.conversation import Conversation
from app.models.experiment import Experiment
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse, MessageResponse
from app.services.assignment_service import get_or_create_assignment
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.hallucination_service import HallucinationService

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def send_message(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    experiment = await db.get(Experiment, req.experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if experiment.status != "active":
        raise HTTPException(status_code=400, detail="Experiment is not active")

    variant = await get_or_create_assignment(db, redis, req.user_id, req.experiment_id, experiment.traffic_split)

    conversation = None
    if req.conversation_id:
        conversation = await db.get(Conversation, req.conversation_id)
        if not conversation or conversation.experiment_id != req.experiment_id:
            raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation:
        conversation = Conversation(
            user_id=req.user_id,
            experiment_id=req.experiment_id,
            title=req.message[:80] + ("..." if len(req.message) > 80 else ""),
        )
        db.add(conversation)
        await db.flush()

    user_msg = Message(
        conversation_id=conversation.id,
        experiment_id=req.experiment_id,
        role="user",
        content=req.message,
    )
    db.add(user_msg)

    rag_service = RAGService(db)
    llm_service = LLMService(db, redis)

    start_time = time.monotonic()

    if variant == "A":
        response_content = await llm_service.generate_baseline(req.message)
        retrieved_chunks = None
    else:
        chunks = await rag_service.retrieve(req.message)
        retrieved_chunks = [{"id": str(c.id), "content": c.content[:200], "score": 0.0} for c in chunks] if chunks else []
        response_content = await llm_service.generate_with_rag(req.message, chunks)

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    assistant_msg = Message(
        conversation_id=conversation.id,
        experiment_id=req.experiment_id,
        role="assistant",
        content=response_content,
        variant=variant,
        latency_ms=elapsed_ms,
        token_count=len(response_content.split()) * 1,
        retrieved_chunk_ids=json.dumps([c["id"] for c in (retrieved_chunks or [])]) if retrieved_chunks else None,
    )
    db.add(assistant_msg)
    await db.flush()

    hallucination_service = HallucinationService(db)
    try:
        await hallucination_service.score_message(
            assistant_msg.id,
            response_content,
            [c["content"] for c in (retrieved_chunks or [])] if retrieved_chunks else None,
        )
    except Exception:
        pass

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_msg.id,
        variant=variant,
        content=response_content,
        latency_ms=elapsed_ms,
        retrieved_chunks=retrieved_chunks or [],
    )


@router.get("/conversations")
async def list_conversations(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .limit(50)
    )
    conversations = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "title": c.title,
            "experiment_id": str(c.experiment_id) if c.experiment_id else None,
            "created_at": c.created_at.isoformat(),
        }
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "experiment_id": str(conversation.experiment_id) if conversation.experiment_id else None,
        "created_at": conversation.created_at.isoformat(),
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "variant": m.variant,
                "latency_ms": m.latency_ms,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conversation)
