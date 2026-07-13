import numpy as np


def precision_at_k(recommended: list[str], relevant: set[str], k: int = 10) -> float:
    recommended_k = recommended[:k]
    if not recommended_k:
        return 0.0
    return len([r for r in recommended_k if r in relevant]) / k


def recall_at_k(recommended: list[str], relevant: set[str], k: int = 10) -> float:
    if not relevant:
        return 0.0
    recommended_k = set(recommended[:k])
    return len(recommended_k & relevant) / len(relevant)


def ndcg_at_k(recommended: list[str], relevant: set[str], k: int = 10) -> float:
    recommended_k = recommended[:k]
    dcg = 0.0
    for i, item in enumerate(recommended_k):
        if item in relevant:
            dcg += 1.0 / np.log2(i + 2)

    ideal = min(len(relevant), k)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(ideal))
    return dcg / idcg if idcg > 0 else 0.0


def hit_rate_at_k(recommended: list[str], relevant: set[str], k: int = 10) -> float:
    return 1.0 if any(r in relevant for r in recommended[:k]) else 0.0


def evaluate_all(recommended: list[str], relevant: set[str], k: int = 10) -> dict:
    return {
        f"Precision@{k}": precision_at_k(recommended, relevant, k),
        f"Recall@{k}": recall_at_k(recommended, relevant, k),
        f"NDCG@{k}": ndcg_at_k(recommended, relevant, k),
        f"HitRate@{k}": hit_rate_at_k(recommended, relevant, k),
    }
