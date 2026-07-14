import uuid
import json

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.message import Message
from app.models.feedback import Feedback
from app.models.document import DocumentChunk


class GovernanceService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_fairness_metrics(self) -> dict:
        result = await self.db.execute(
            select(
                Message.variant,
                func.count(Message.id),
            )
            .where(
                Message.role == "assistant",
                Message.variant.isnot(None),
            )
            .group_by(Message.variant)
        )
        total_counts = {row[0]: row[1] for row in result}

        result = await self.db.execute(
            select(
                Message.variant,
                func.avg(Feedback.rating),
                func.count(Feedback.id),
            )
            .join(Feedback, Feedback.message_id == Message.id)
            .where(
                Message.role == "assistant",
                Message.variant.isnot(None),
                Feedback.rating.isnot(None),
            )
            .group_by(Message.variant)
        )
        rating_data = {}
        for row in result:
            rating_data[row[0]] = {
                "avg_rating": round(float(row[1]), 4) if row[1] else 0,
                "rated_count": row[2],
            }

        variants = set(list(total_counts.keys()) + list(rating_data.keys()))
        metrics = {}
        for v in sorted(variants):
            metrics[v] = {
                "total_messages": total_counts.get(v, 0),
                "avg_rating": rating_data.get(v, {}).get("avg_rating", 0),
                "rated_count": rating_data.get(v, {}).get("rated_count", 0),
            }

        fairness_gap = 0.0
        ratings = [m["avg_rating"] for m in metrics.values() if m["rated_count"] > 0]
        if len(ratings) >= 2:
            fairness_gap = round(max(ratings) - min(ratings), 4)

        return {
            "metrics_by_variant": metrics,
            "fairness_gap": fairness_gap,
            "note": "Fairness gap is the difference in avg rating between best and worst performing variant. "
                    "Extend by adding demographic/condition tags for health equity monitoring.",
        }

    async def get_audit_log(self, limit: int = 100) -> list[dict]:
        result = await self.db.execute(
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        logs = result.scalars().all()
        return [
            {
                "id": str(log.id),
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details_json,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]

    async def get_transparency(self, message_id: uuid.UUID) -> dict:
        message = await self.db.get(Message, message_id)
        if not message:
            return {"error": "Message not found"}

        info = {
            "message_id": str(message.id),
            "variant": message.variant,
            "content_preview": message.content[:500] if message.content else "",
            "latency_ms": message.latency_ms,
            "token_count": message.token_count,
            "created_at": message.created_at.isoformat(),
        }

        if message.retrieved_chunk_ids:
            try:
                chunk_ids = json.loads(message.retrieved_chunk_ids)
                chunks = []
                for cid in chunk_ids:
                    try:
                        chunk = await self.db.get(DocumentChunk, uuid.UUID(cid))
                        if chunk:
                            chunks.append({
                                "id": str(chunk.id),
                                "filename": chunk.filename,
                                "content_preview": chunk.content[:300],
                            })
                    except (ValueError, Exception):
                        pass
                info["retrieved_chunks"] = chunks
            except (json.JSONDecodeError, Exception):
                info["retrieved_chunks"] = []

        if message.prompt_template:
            info["prompt_template"] = message.prompt_template[:1000]

        return info
