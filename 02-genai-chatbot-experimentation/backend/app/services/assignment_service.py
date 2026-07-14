import hashlib
import uuid

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment
from app.settings.config import get_settings

settings = get_settings()


async def get_or_create_assignment(
    db: AsyncSession,
    redis: Redis,
    user_id: uuid.UUID,
    experiment_id: uuid.UUID,
    traffic_split: float,
) -> str:
    cache_key = f"assign:{user_id}:{experiment_id}"

    cached = await redis.get(cache_key)
    if cached in ("A", "B"):
        return cached

    result = await db.execute(
        select(Assignment).where(
            Assignment.user_id == user_id,
            Assignment.experiment_id == experiment_id,
        )
    )
    assignment = result.scalar_one_or_none()

    if assignment:
        await redis.setex(cache_key, 86400, assignment.variant)
        return assignment.variant

    hash_input = f"{user_id}:{experiment_id}:{settings.ASSIGNMENT_SALT}"
    hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()
    hash_int = int(hash_digest[:16], 16)
    max_int = 0xFFFFFFFFFFFFFFFF
    variant = "A" if (hash_int / max_int) < traffic_split else "B"

    assignment = Assignment(
        user_id=user_id,
        experiment_id=experiment_id,
        variant=variant,
    )
    db.add(assignment)
    await db.flush()

    await redis.setex(cache_key, 86400, variant)

    return variant
