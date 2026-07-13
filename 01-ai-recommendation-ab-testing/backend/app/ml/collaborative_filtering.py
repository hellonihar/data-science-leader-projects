import uuid

import numpy as np

from app.ml.base_model import BaseRecommendationModel
from app.models.item import Item


class CollaborativeFilteringModel(BaseRecommendationModel):
    def __init__(self):
        self.user_factors = None
        self.item_factors = None
        self.item_ids = None
        self.user_map = {}
        self.item_map = {}

    def fit(self, user_ids: list[str], item_ids: list[str], ratings: list[float],
            n_factors: int = 20, n_epochs: int = 20, lr: float = 0.01, reg: float = 0.02):
        unique_users = list(set(user_ids))
        unique_items = list(set(item_ids))
        self.user_map = {uid: i for i, uid in enumerate(unique_users)}
        self.item_map = {iid: i for i, iid in enumerate(unique_items)}
        n_users = len(unique_users)
        n_items = len(unique_items)

        rng = np.random.RandomState(42)
        self.user_factors = rng.randn(n_users, n_factors) * 0.1
        self.item_factors = rng.randn(n_items, n_factors) * 0.1
        user_bias = np.zeros(n_users)
        item_bias = np.zeros(n_items)
        global_bias = np.mean(ratings) if ratings else 0.0

        for epoch in range(n_epochs):
            for uid, iid, r in zip(user_ids, item_ids, ratings):
                u_idx = self.user_map[uid]
                i_idx = self.item_map[iid]
                pred = global_bias + user_bias[u_idx] + item_bias[i_idx] + np.dot(
                    self.user_factors[u_idx], self.item_factors[i_idx]
                )
                err = r - pred

                user_bias[u_idx] += lr * (err - reg * user_bias[u_idx])
                item_bias[i_idx] += lr * (err - reg * item_bias[i_idx])

                uf = self.user_factors[u_idx].copy()
                self.user_factors[u_idx] += lr * (
                    err * self.item_factors[i_idx] - reg * self.user_factors[u_idx]
                )
                self.item_factors[i_idx] += lr * (
                    err * uf - reg * self.item_factors[i_idx]
                )

        self.item_ids = list(unique_items)

    def recommend(self, user_id: uuid.UUID, items: list[Item], top_k: int = 10) -> list[Item]:
        uid_str = str(user_id)
        if self.user_factors is None or uid_str not in self.user_map:
            return items[:top_k]

        u_idx = self.user_map[uid_str]
        scores = []
        for item in items:
            iid_str = str(item.id)
            if iid_str in self.item_map:
                i_idx = self.item_map[iid_str]
                score = float(np.dot(self.user_factors[u_idx], self.item_factors[i_idx]))
            else:
                score = 0.0
            item.score = score
            scores.append((item, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scores[:top_k]]
