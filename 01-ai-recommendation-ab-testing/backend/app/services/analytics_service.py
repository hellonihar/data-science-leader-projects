import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.statistics import compute_ab_test_significance
from app.models.experiment import Experiment
from app.models.interaction import Interaction


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_experiment_analytics(self, experiment_id: uuid.UUID) -> dict | None:
        experiment = await self.session.get(Experiment, experiment_id)
        if not experiment:
            return None

        variants = []
        for variant_label in ("A", "B"):
            metrics = await self._compute_variant_metrics(experiment_id, variant_label)
            variants.append(metrics)

        result = {
            "experiment_id": experiment_id,
            "experiment_name": experiment.name,
            "status": experiment.status,
            "variants": variants,
            "winner": None,
            "p_value": None,
            "significant": None,
            "revenue_lift": None,
            "ctr_lift": None,
            "updated_at": datetime.now(timezone.utc),
        }

        if len(variants) >= 2 and variants[0]["total_impressions"] > 0 and variants[1]["total_impressions"] > 0:
            clicks_a = variants[0]["total_clicks"]
            impressions_a = variants[0]["total_impressions"]
            clicks_b = variants[1]["total_clicks"]
            impressions_b = variants[1]["total_impressions"]

            significance = compute_ab_test_significance(
                clicks_a, impressions_a, clicks_b, impressions_b
            )
            result["p_value"] = significance["p_value"]
            result["significant"] = significance["significant"]
            result["ctr_lift"] = significance["lift"]

            rev_a = variants[0]["total_revenue"]
            rev_b = variants[1]["total_revenue"]
            if rev_a > 0:
                result["revenue_lift"] = (rev_b - rev_a) / rev_a

            if result["significant"]:
                ctr_a = variants[0]["ctr"]
                ctr_b = variants[1]["ctr"]
                result["winner"] = "A" if ctr_b <= ctr_a else "B"

        return result

    async def _compute_variant_metrics(self, experiment_id: uuid.UUID, variant: str) -> dict:
        base = select(Interaction).where(
            Interaction.experiment_id == experiment_id,
            Interaction.variant == variant,
        )

        impressions = await self._count_by_type(base, "impression")
        clicks = await self._count_by_type(base, "click")
        conversions = await self._count_by_type(base, "purchase")
        revenue = await self._sum_revenue(base)

        unique_users_result = await self.session.execute(
            select(func.count(func.distinct(Interaction.user_id))).where(
                Interaction.experiment_id == experiment_id,
                Interaction.variant == variant,
            )
        )
        total_users = unique_users_result.scalar() or 0

        return {
            "variant": variant,
            "total_users": total_users,
            "total_impressions": impressions,
            "total_clicks": clicks,
            "total_conversions": conversions,
            "total_revenue": revenue,
            "ctr": clicks / impressions if impressions > 0 else 0.0,
            "conversion_rate": conversions / impressions if impressions > 0 else 0.0,
            "revenue_per_user": revenue / total_users if total_users > 0 else 0.0,
        }

    async def _count_by_type(self, base_query, interaction_type: str) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(
                base_query.filter(Interaction.interaction_type == interaction_type).subquery()
            )
        )
        return result.scalar() or 0

    async def _sum_revenue(self, base_query) -> float:
        result = await self.session.execute(
            select(func.coalesce(func.sum(Interaction.revenue), 0)).where(
                Interaction.experiment_id.in_(
                    select(Interaction.experiment_id).where(
                        Interaction.interaction_type == "purchase"
                    )
                )
            )
        )
        return float(result.scalar() or 0.0)
