import uuid

import numpy as np

from app.ml.base_model import BaseRecommendationModel
from app.models.item import Item


class DeepLearningModel(BaseRecommendationModel):
    def __init__(self):
        self.user_embeddings = None
        self.item_embeddings = None
        self.user_map = {}
        self.item_map = {}
        self.embedding_dim = 32

    def fit(self, user_ids: list[str], item_ids: list[str], ratings: list[float],
            n_epochs: int = 30, lr: float = 0.01, reg: float = 0.01):
        unique_users = list(set(user_ids))
        unique_items = list(set(item_ids))
        self.user_map = {uid: i for i, uid in enumerate(unique_users)}
        self.item_map = {iid: i for i, iid in enumerate(unique_items)}
        n_users = len(unique_users)
        n_items = len(unique_items)

        rng = np.random.RandomState(42)
        self.user_embeddings = rng.randn(n_users, self.embedding_dim) * 0.1
        self.item_embeddings = rng.randn(n_items, self.embedding_dim) * 0.1

        for epoch in range(n_epochs):
            indices = rng.permutation(len(user_ids))
            for idx in indices:
                u_idx = self.user_map[user_ids[idx]]
                i_idx = self.item_map[item_ids[idx]]
                r = ratings[idx]

                elementwise = self.user_embeddings[u_idx] * self.item_embeddings[i_idx]
                mlp_hidden = np.maximum(elementwise, 0)
                pred = float(np.sum(mlp_hidden))
                err = r - pred

                grad = -2.0 * err
                relu_mask = (elementwise > 0).astype(float)

                grad_u = grad * (self.item_embeddings[i_idx] * relu_mask) + reg * self.user_embeddings[u_idx]
                grad_i = grad * (self.user_embeddings[u_idx] * relu_mask) + reg * self.item_embeddings[i_idx]

                self.user_embeddings[u_idx] -= lr * grad_u
                self.item_embeddings[i_idx] -= lr * grad_i

        self._item_ids = list(unique_items)

    def recommend(self, user_id: uuid.UUID, items: list[Item], top_k: int = 10) -> list[Item]:
        uid_str = str(user_id)
        if self.user_embeddings is None or uid_str not in self.user_map:
            return items[:top_k]

        u_idx = self.user_map[uid_str]
        scores = []
        for item in items:
            iid_str = str(item.id)
            if iid_str in self.item_map:
                i_idx = self.item_map[iid_str]
                elementwise = self.user_embeddings[u_idx] * self.item_embeddings[i_idx]
                score = float(np.sum(np.maximum(elementwise, 0)))
            else:
                score = 0.0
            item.score = score
            scores.append((item, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scores[:top_k]]
