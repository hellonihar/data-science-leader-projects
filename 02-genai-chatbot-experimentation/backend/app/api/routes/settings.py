from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.settings_service import SettingsService, ALLOWED_CATEGORIES


class SettingUpdate(BaseModel):
    value: str = Field(..., min_length=0, max_length=1000)


class CategoryReset(BaseModel):
    category: str


router = APIRouter()


@router.get("")
async def list_settings(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if category and category not in ALLOWED_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category. Allowed: {ALLOWED_CATEGORIES}")
    service = SettingsService(db)
    return await service.get_registry()


@router.get("/{key}")
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    service = SettingsService(db)
    setting = await service.get(key)
    if not setting:
        registry = await service.get_registry()
        for entry in registry:
            if entry["key"] == key:
                return entry
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    return setting


@router.put("/{key}")
async def update_setting(
    key: str,
    req: SettingUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = SettingsService(db)
    setting = await service.set(key, req.value)
    return setting


@router.post("/reset/{key}")
async def reset_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    service = SettingsService(db)
    setting = await service.reset_to_default(key)
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    return setting


@router.post("/reset-category")
async def reset_category(
    req: CategoryReset,
    db: AsyncSession = Depends(get_db),
):
    if req.category not in ALLOWED_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category. Allowed: {ALLOWED_CATEGORIES}")
    service = SettingsService(db)
    count = await service.reset_category(req.category)
    return {"message": f"Reset {count} settings in category '{req.category}'"}
