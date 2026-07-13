import math


def compute_ab_test_significance(
    clicks_a: int, impressions_a: int,
    clicks_b: int, impressions_b: int,
) -> dict:
    if impressions_a == 0 or impressions_b == 0:
        return {"p_value": 1.0, "significant": False, "lift": 0.0, "z_score": 0.0}

    p_a = clicks_a / impressions_a
    p_b = clicks_b / impressions_b
    p_pooled = (clicks_a + clicks_b) / (impressions_a + impressions_b)

    se = math.sqrt(p_pooled * (1 - p_pooled) * (1 / impressions_a + 1 / impressions_b))
    if se == 0:
        return {"p_value": 1.0, "significant": False, "lift": 0.0, "z_score": 0.0}

    z = (p_b - p_a) / se
    p_value = 2 * (1 - _normal_cdf(abs(z)))
    lift = (p_b - p_a) / p_a if p_a > 0 else 0.0

    return {
        "p_value": round(p_value, 6),
        "z_score": round(z, 4),
        "significant": p_value < 0.05,
        "lift": round(lift, 6),
    }


def _normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))
