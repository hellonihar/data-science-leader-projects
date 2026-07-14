import uuid
import math
from collections import defaultdict

from scipy import stats as scipy_stats
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.models.feedback import Feedback
from app.models.hallucination import HallucinationScore
from app.models.experiment import Experiment
from app.settings.config import get_settings
from app.services.settings_service import SettingsService

settings = get_settings()


class AnalyticsService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self._settings_service = SettingsService(db)

    async def get_experiment_metrics(self, experiment_id: uuid.UUID) -> dict:
        experiment = await self.db.get(Experiment, experiment_id)
        if not experiment:
            return {"error": "Experiment not found"}

        result = await self.db.execute(
            select(Message)
            .where(
                Message.experiment_id == experiment_id,
                Message.role == "assistant",
                Message.variant.isnot(None),
            )
        )
        messages = list(result.scalars().all())

        grouped = defaultdict(list)
        for m in messages:
            grouped[m.variant].append(m)

        metrics = {}
        for variant, variant_messages in grouped.items():
            msg_ids = [m.id for m in variant_messages]

            feedback_result = await self.db.execute(
                select(Feedback).where(Feedback.message_id.in_(msg_ids))
            )
            feedbacks = list(feedback_result.scalars().all())

            resolution_threshold = int(
                await self._settings_service.get_typed_value("feedback_resolution_threshold")
                or settings.FEEDBACK_RESOLUTION_THRESHOLD
            )

            resolved = sum(1 for f in feedbacks if f.rating is not None and f.rating >= resolution_threshold)
            total_rated = sum(1 for f in feedbacks if f.rating is not None)
            resolution_rate = resolved / total_rated if total_rated > 0 else 0.0

            avg_rating = (
                sum(f.rating for f in feedbacks if f.rating is not None) / total_rated
                if total_rated > 0
                else 0.0
            )

            hallucination_result = await self.db.execute(
                select(HallucinationScore).where(
                    HallucinationScore.message_id.in_(msg_ids)
                )
            )
            hallu_scores = list(hallucination_result.scalars().all())
            avg_hallu = (
                sum(h.score for h in hallu_scores) / len(hallu_scores)
                if hallu_scores
                else 0.0
            )

            latencies = [m.latency_ms for m in variant_messages if m.latency_ms is not None]
            avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0.0

            token_counts = [m.token_count for m in variant_messages if m.token_count is not None]
            avg_tokens = sum(token_counts) / len(token_counts) if token_counts else 0.0

            metrics[variant] = {
                "message_count": len(variant_messages),
                "resolution_rate": round(resolution_rate, 4),
                "resolved_count": resolved,
                "total_rated": total_rated,
                "avg_rating": round(avg_rating, 4),
                "avg_hallucination_score": round(avg_hallu, 4),
                "avg_latency_ms": round(avg_latency, 2),
                "p95_latency_ms": round(p95_latency, 2),
                "avg_token_count": round(avg_tokens, 2),
            }

        stats = await self._compute_statistics(metrics)

        return {
            "experiment_id": str(experiment_id),
            "experiment_name": experiment.name,
            "experiment_status": experiment.status,
            "metrics": metrics,
            "statistical_significance": stats,
        }

    async def _compute_statistics(self, metrics: dict) -> dict:
        result = {}

        if "A" in metrics and "B" in metrics:
            a = metrics["A"]
            b = metrics["B"]

            if a["total_rated"] > 0 and b["total_rated"] > 0:
                chi2_alpha = float(
                    await self._settings_service.get_typed_value("stats_chisq_alpha")
                    or settings.STATS_CHISQ_ALPHA
                )
                obs = [
                    [a["resolved_count"], a["total_rated"] - a["resolved_count"]],
                    [b["resolved_count"], b["total_rated"] - b["resolved_count"]],
                ]
                if obs[0][0] + obs[0][1] > 0 and obs[1][0] + obs[1][1] > 0:
                    try:
                        chi2, p_value = scipy_stats.chi2_contingency(obs)[:2]
                        result["resolution_rate"] = {
                            "test": "chi-square",
                            "chi2_stat": round(float(chi2), 4),
                            "p_value": round(float(p_value), 4),
                            "significant": bool(p_value < chi2_alpha),
                            "alpha": chi2_alpha,
                        }
                    except Exception:
                        pass

            ttest_alpha = float(
                await self._settings_service.get_typed_value("stats_ttest_alpha")
                or settings.STATS_TTEST_ALPHA
            )
            result["latency"] = {
                "note": "T-test requires per-message data; run with full dataset",
                "alpha": ttest_alpha,
            }

            result["hallucination"] = {
                "note": "T-test requires per-message data; run with full dataset",
                "alpha": ttest_alpha,
            }

        return result

    async def get_hallucination_distribution(self) -> dict:
        result = await self.db.execute(
            select(
                HallucinationScore.category,
                func.count(HallucinationScore.id),
            ).group_by(HallucinationScore.category)
        )
        distribution = {row[0]: row[1] for row in result}
        return {"distribution": distribution}

    async def get_latency_comparison(self) -> dict:
        result = await self.db.execute(
            select(
                Message.variant,
                func.avg(Message.latency_ms),
                func.percentile_cont(0.5).within_group(Message.latency_ms.asc()),
                func.percentile_cont(0.95).within_group(Message.latency_ms.asc()),
                func.count(Message.id),
            ).where(
                Message.role == "assistant",
                Message.variant.isnot(None),
                Message.latency_ms.isnot(None),
            ).group_by(Message.variant)
        )
        rows = result.all()
        return {
            str(row.variant): {
                "avg_ms": round(float(row[1]), 2) if row[1] else 0,
                "median_ms": round(float(row[2]), 2) if row[2] else 0,
                "p95_ms": round(float(row[3]), 2) if row[3] else 0,
                "count": row[4],
            }
            for row in rows
        }
