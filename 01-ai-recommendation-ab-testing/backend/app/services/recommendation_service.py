import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.ml.collaborative_filtering import CollaborativeFilteringModel
from app.ml.deep_learning import DeepLearningModel
from app.ml.model_registry import ModelRegistry
from app.services.experiment_service import ExperimentService


class RecommendationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.experiment_service = ExperimentService(session)
        self.model_registry = ModelRegistry()

    async def get_recommendations(
        self, user_id: uuid.UUID, top_k: int = 10
    ) -> dict:
        experiment = await self.experiment_service.get_active_experiment()
        variant = "A"
        model_name = "collaborative_filtering"
        experiment_id = None

        if experiment:
            experiment_id = experiment.id
            variant = await self.experiment_service.assign_user(user_id, experiment.id)
            model_name = (
                experiment.variant_a_label if variant == "A"
                else experiment.variant_b_label
            )

        all_items = await self._get_all_items()
        if not all_items:
            return {"user_id": user_id, "variant": variant, "recommendations": [], "model": model_name}

        model = self.model_registry.load_model(model_name)
        if model is None:
            recommendations = all_items[:top_k]
        else:
            scored = model.recommend(user_id, all_items, top_k)
            recommendations = scored

        result_items = []
        for item in recommendations:
            result_items.append({
                "item_id": item.id,
                "name": item.name,
                "category": item.category,
                "price": item.price,
                "score": getattr(item, "score", 0.0),
            })

        return {
            "user_id": user_id,
            "variant": variant,
            "experiment_id": experiment_id,
            "recommendations": result_items,
            "model": model_name,
        }

    async def _get_all_items(self) -> list[Item]:
        result = await self.session.execute(select(Item).limit(100))
        return list(result.scalars().all())
