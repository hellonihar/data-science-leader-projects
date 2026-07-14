import json
import uuid
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hallucination import HallucinationScore
from app.settings.config import get_settings
from app.services.settings_service import SettingsService

settings = get_settings()


class HallucinationService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self._settings_service = SettingsService(db)
        self._nli_model = None

    async def _get_nli_model(self):
        if self._nli_model is None:
            try:
                from transformers import pipeline
                model_name = settings.HALLUCINATION_MODEL
                self._nli_model = pipeline(
                    "text-classification",
                    model=model_name,
                    top_k=None,
                )
            except ImportError:
                raise RuntimeError(
                    "transformers not installed. "
                    "Run: pip install transformers torch"
                )
        return self._nli_model

    def _decompose_claims(self, response: str) -> list[str]:
        sentences = re.split(r'(?<=[.!?])\s+', response.strip())
        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                claims.append(sentence)
        return claims

    def _claim_has_factual_content(self, claim: str) -> bool:
        claim_lower = claim.lower()
        non_factual_patterns = [
            "thank", "please", "welcome", "sorry", "unfortunately",
            "i think", "i believe", "in my opinion", "i hope",
        ]
        for pattern in non_factual_patterns:
            if pattern in claim_lower:
                return False
        return True

    async def score_message(
        self,
        message_id: uuid.UUID,
        response: str,
        source_chunks: list[str] | None,
    ) -> HallucinationScore:
        enabled = await self._settings_service.get_typed_value("hallucination_score_enabled")
        if enabled is not None and not bool(enabled):
            return HallucinationScore(
                message_id=message_id,
                score=1.0,
                category="Consistent",
                details_json=json.dumps({"note": "Scoring disabled by settings"}),
            )

        entailment_threshold = float(
            await self._settings_service.get_typed_value("hallucination_entailment_threshold")
            or settings.HALLUCINATION_ENTAILMENT_THRESHOLD
        )
        contradiction_tolerance = float(
            await self._settings_service.get_typed_value("hallucination_contradiction_tolerance")
            or settings.HALLUCINATION_CONTRADICTION_TOLERANCE
        )

        claims = self._decompose_claims(response)
        claims = [c for c in claims if self._claim_has_factual_content(c)]

        if not claims:
            score = HallucinationScore(
                message_id=message_id,
                score=1.0,
                category="Consistent",
                details_json=json.dumps({"note": "No factual claims detected in response"}),
            )
            self.db.add(score)
            await self.db.flush()
            return score

        detail_results = []

        if source_chunks:
            for claim in claims:
                best_support = 0.0
                best_contradiction = 0.0
                best_source = ""
                best_label = "Neutral"

                for source in source_chunks:
                    label, entail_prob, contra_prob = await self._classify_nli(claim, source)
                    if entail_prob > best_support:
                        best_support = entail_prob
                        best_contradiction = contra_prob
                        best_source = source[:200]
                        best_label = label

                detail_results.append({
                    "claim": claim,
                    "label": best_label,
                    "entailment_prob": round(best_support, 4),
                    "contradiction_prob": round(best_contradiction, 4),
                    "source_excerpt": best_source,
                })
        else:
            for claim in claims:
                detail_results.append({
                    "claim": claim,
                    "label": "Neutral",
                    "entailment_prob": 0.5,
                    "contradiction_prob": 0.0,
                    "source_excerpt": "No source chunks available (Baseline variant)",
                })

        total = len(detail_results)
        entail_count = sum(1 for d in detail_results if d["label"] == "Entailment")
        contradiction_count = sum(1 for d in detail_results if d["label"] == "Contradiction")

        entail_ratio = entail_count / total if total > 0 else 1.0
        contradiction_ratio = contradiction_count / total if total > 0 else 0.0

        if contradiction_ratio > contradiction_tolerance:
            category = "Major Hallucination"
            n_score = max(0.0, 1.0 - contradiction_ratio)
        elif entail_ratio >= entailment_threshold:
            category = "Consistent"
            n_score = entail_ratio
        else:
            category = "Minor Inconsistency"
            n_score = entail_ratio

        score = HallucinationScore(
            message_id=message_id,
            score=round(n_score, 4),
            category=category,
            details_json=json.dumps({
                "claim_count": total,
                "entail_ratio": round(entail_ratio, 4),
                "contradiction_ratio": round(contradiction_ratio, 4),
                "entailment_threshold": entailment_threshold,
                "contradiction_tolerance": contradiction_tolerance,
                "claims": detail_results,
            }),
        )
        self.db.add(score)
        await self.db.flush()
        return score

    async def _classify_nli(self, premise: str, hypothesis: str) -> tuple[str, float, float]:
        try:
            model = await self._get_nli_model()
            result = model(f"{premise} </s> {hypothesis}")
            if isinstance(result, list) and isinstance(result[0], list):
                scores = {item["label"]: item["score"] for item in result[0]}
            elif isinstance(result, list) and isinstance(result[0], dict):
                scores = {item["label"]: item["score"] for item in result}
            else:
                return "Neutral", 0.5, 0.0

            entail_prob = scores.get("ENTAILMENT", scores.get("entailment", 0.0))
            contra_prob = scores.get("CONTRADICTION", scores.get("contradiction", 0.0))

            if entail_prob > contra_prob and entail_prob > 0.5:
                return "Entailment", entail_prob, contra_prob
            elif contra_prob > entail_prob and contra_prob > 0.5:
                return "Contradiction", entail_prob, contra_prob
            else:
                return "Neutral", entail_prob, contra_prob
        except Exception:
            return "Neutral", 0.5, 0.0
