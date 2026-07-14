from fastapi import APIRouter

from app.api.routes import analytics, chat, documents, experiments, feedback, governance, settings

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(governance.router, prefix="/governance", tags=["governance"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
