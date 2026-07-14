from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.feedback import Feedback
from app.models.message import Message
from app.schemas.feedback import FeedbackCreate

router = APIRouter()


@router.post("", status_code=201)
async def submit_feedback(
    req: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
):
    message = await db.get(Message, req.message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    feedback = Feedback(
        message_id=req.message_id,
        rating=req.rating,
        thumbs_up=req.thumbs_up,
    )
    db.add(feedback)
    await db.flush()

    return {"id": str(feedback.id), "message_id": str(req.message_id)}
