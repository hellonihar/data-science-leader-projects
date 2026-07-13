import abc
import uuid

from app.models.item import Item


class BaseRecommendationModel(abc.ABC):
    @abc.abstractmethod
    def recommend(self, user_id: uuid.UUID, items: list[Item], top_k: int = 10) -> list[Item]:
        ...
