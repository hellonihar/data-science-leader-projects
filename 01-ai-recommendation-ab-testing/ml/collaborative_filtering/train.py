import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.ml.collaborative_filtering import CollaborativeFilteringModel
from app.ml.model_registry import ModelRegistry


def generate_sample_data(n_users: int = 100, n_items: int = 50, n_ratings: int = 2000):
    rng = np.random.RandomState(42)
    user_ids = [f"user_{i:03d}" for i in range(n_users)]
    item_ids = [f"item_{i:03d}" for i in range(n_items)]

    sampled_users = rng.choice(user_ids, n_ratings)
    sampled_items = rng.choice(item_ids, n_ratings)

    latent = rng.randn(n_users, 5) @ rng.randn(5, n_items)
    latent = (latent - latent.min()) / (latent.max() - latent.min()) * 4 + 1

    ratings = []
    for u, i in zip(sampled_users, sampled_items):
        u_idx = user_ids.index(u)
        i_idx = item_ids.index(i)
        base = latent[u_idx, i_idx]
        noise = rng.randn() * 0.5
        ratings.append(max(1, min(5, round(base + noise))))

    return user_ids, item_ids, sampled_users, sampled_items, ratings


def main():
    print("Generating sample interaction data...")
    user_ids, item_ids, sampled_users, sampled_items, ratings = generate_sample_data()

    print(f"Training collaborative filtering model on {len(ratings)} interactions...")
    model = CollaborativeFilteringModel()
    model.fit(
        list(sampled_users),
        list(sampled_items),
        ratings,
        n_factors=20,
        n_epochs=20,
    )

    registry = ModelRegistry()
    registry.save_model("collaborative_filtering", model)
    print("Model saved to registry as 'collaborative_filtering'")


if __name__ == "__main__":
    main()
