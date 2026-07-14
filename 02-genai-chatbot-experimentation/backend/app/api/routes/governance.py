import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.governance_service import GovernanceService

router = APIRouter()


@router.get("/fairness")
async def get_fairness_metrics(
    db: AsyncSession = Depends(get_db),
):
    service = GovernanceService(db)
    return await service.get_fairness_metrics()


@router.get("/audit")
async def get_audit_log(
    db: AsyncSession = Depends(get_db),
):
    service = GovernanceService(db)
    return await service.get_audit_log()


@router.get("/transparency/{message_id}")
async def get_transparency(
    message_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = GovernanceService(db)
    return await service.get_transparency(message_id)
