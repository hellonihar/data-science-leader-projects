from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import DynamicSetting
from app.settings.config import get_settings

env_settings = get_settings()


SETTING_REGISTRY: dict[str, dict] = {
    "hallucination_entailment_threshold": {
        "default": str(env_settings.HALLUCINATION_ENTAILMENT_THRESHOLD),
        "value_type": "float",
        "label": "Hallucination Entailment Threshold",
        "description": "Minimum entailment ratio (0-1) for a response to be considered Consistent. Higher = stricter.",
        "category": "hallucination",
        "min_value": 0.0,
        "max_value": 1.0,
    },
    "hallucination_contradiction_tolerance": {
        "default": str(env_settings.HALLUCINATION_CONTRADICTION_TOLERANCE),
        "value_type": "float",
        "label": "Contradiction Tolerance",
        "description": "Maximum allowed contradiction ratio (0-1) before flagging as Major Hallucination. 0 = zero tolerance.",
        "category": "hallucination",
        "min_value": 0.0,
        "max_value": 1.0,
    },
    "hallucination_score_enabled": {
        "default": str(env_settings.HALLUCINATION_SCORE_ENABLED),
        "value_type": "bool",
        "label": "Hallucination Scoring Enabled",
        "description": "Enable or disable automated hallucination scoring on responses.",
        "category": "hallucination",
    },
    "rag_top_k": {
        "default": str(env_settings.RAG_TOP_K),
        "value_type": "int",
        "label": "RAG Top-K Documents",
        "description": "Number of document chunks to retrieve per query. Higher = more context, slower response.",
        "category": "rag",
        "min_value": 1.0,
        "max_value": 50.0,
    },
    "rag_chunk_size": {
        "default": str(env_settings.RAG_CHUNK_SIZE),
        "value_type": "int",
        "label": "RAG Chunk Size (characters)",
        "description": "Maximum characters per document chunk for indexing.",
        "category": "rag",
        "min_value": 64.0,
        "max_value": 4096.0,
    },
    "rag_chunk_overlap": {
        "default": str(env_settings.RAG_CHUNK_OVERLAP),
        "value_type": "int",
        "label": "RAG Chunk Overlap (characters)",
        "description": "Character overlap between consecutive chunks to preserve context boundaries.",
        "category": "rag",
        "min_value": 0.0,
        "max_value": 1024.0,
    },
    "groq_model_baseline": {
        "default": env_settings.GROQ_MODEL_BASELINE,
        "value_type": "str",
        "label": "Baseline Model Name",
        "description": "Groq model ID used for Baseline variant (Variant A).",
        "category": "llm",
    },
    "groq_model_finetuned": {
        "default": env_settings.GROQ_MODEL_FINETUNED,
        "value_type": "str",
        "label": "Fine-tuned Model Name",
        "description": "Groq model ID used for Fine-tuned + RAG variant (Variant B).",
        "category": "llm",
    },
    "groq_temperature": {
        "default": str(env_settings.GROQ_TEMPERATURE),
        "value_type": "float",
        "label": "LLM Temperature",
        "description": "Response randomness (0 = deterministic, 1 = creative).",
        "category": "llm",
        "min_value": 0.0,
        "max_value": 2.0,
    },
    "groq_max_tokens": {
        "default": str(env_settings.GROQ_MAX_TOKENS),
        "value_type": "int",
        "label": "Max Tokens Per Response",
        "description": "Maximum tokens the LLM can generate in a single response.",
        "category": "llm",
        "min_value": 64.0,
        "max_value": 8192.0,
    },
    "feedback_resolution_threshold": {
        "default": str(env_settings.FEEDBACK_RESOLUTION_THRESHOLD),
        "value_type": "int",
        "label": "Resolution Rating Threshold",
        "description": "Minimum rating (1-5) that counts as a 'resolved' conversation.",
        "category": "analytics",
        "min_value": 1.0,
        "max_value": 5.0,
    },
    "stats_chisq_alpha": {
        "default": str(env_settings.STATS_CHISQ_ALPHA),
        "value_type": "float",
        "label": "Chi-Square Significance Alpha",
        "description": "P-value threshold for statistical significance of resolution rate differences.",
        "category": "analytics",
        "min_value": 0.001,
        "max_value": 0.1,
    },
    "stats_ttest_alpha": {
        "default": str(env_settings.STATS_TTEST_ALPHA),
        "value_type": "float",
        "label": "T-Test Significance Alpha",
        "description": "P-value threshold for statistical significance of continuous metrics (latency, hallucination).",
        "category": "analytics",
        "min_value": 0.001,
        "max_value": 0.1,
    },
    "experiment_default_traffic_split": {
        "default": str(env_settings.EXPERIMENT_DEFAULT_TRAFFIC_SPLIT),
        "value_type": "float",
        "label": "Default Traffic Split",
        "description": "Proportion of users assigned to Variant A (0-1). 0.5 = equal split.",
        "category": "experiment",
        "min_value": 0.0,
        "max_value": 1.0,
    },
    "embedding_model": {
        "default": env_settings.EMBEDDING_MODEL,
        "value_type": "str",
        "label": "Embedding Model",
        "description": "Sentence-transformer model name for document embedding generation.",
        "category": "rag",
    },
}

ALLOWED_CATEGORIES = ["hallucination", "rag", "llm", "analytics", "experiment", "general"]


class SettingsService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, category: str | None = None) -> list[DynamicSetting]:
        query = select(DynamicSetting).where(DynamicSetting.is_active == True)
        if category:
            query = query.where(DynamicSetting.category == category)
        query = query.order_by(DynamicSetting.category, DynamicSetting.key)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get(self, key: str) -> DynamicSetting | None:
        result = await self.db.execute(
            select(DynamicSetting).where(
                DynamicSetting.key == key,
                DynamicSetting.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def set(self, key: str, value: str) -> DynamicSetting:
        setting = await self.get(key)
        if setting:
            setting.value = value
        else:
            meta = SETTING_REGISTRY.get(key, {})
            setting = DynamicSetting(
                id=key,
                key=key,
                value=value,
                value_type=meta.get("value_type", "str"),
                label=meta.get("label", key),
                description=meta.get("description", ""),
                category=meta.get("category", "general"),
                min_value=meta.get("min_value"),
                max_value=meta.get("max_value"),
            )
            self.db.add(setting)
        await self.db.flush()
        return setting

    async def get_typed_value(self, key: str) -> str | int | float | bool | None:
        setting = await self.get(key)
        if setting is None:
            meta = SETTING_REGISTRY.get(key)
            if not meta:
                return None
            return self._cast(meta["default"], meta["value_type"])
        return self._cast(setting.value, setting.value_type)

    async def get_registry(self) -> list[dict]:
        existing = {s.key: s for s in await self.get_all()}
        result = []
        for key, meta in SETTING_REGISTRY.items():
            entry = {**meta, "key": key}
            if key in existing:
                entry["current_value"] = existing[key].value
            else:
                entry["current_value"] = meta["default"]
            result.append(entry)
        return result

    async def reset_to_default(self, key: str) -> DynamicSetting | None:
        meta = SETTING_REGISTRY.get(key)
        if not meta:
            return None
        return await self.set(key, meta["default"])

    async def reset_category(self, category: str) -> int:
        count = 0
        for key, meta in SETTING_REGISTRY.items():
            if meta.get("category") == category:
                await self.set(key, meta["default"])
                count += 1
        return count

    def _cast(self, value: str, value_type: str) -> str | int | float | bool:
        if value_type == "int":
            return int(value)
        elif value_type == "float":
            return float(value)
        elif value_type == "bool":
            return value.lower() in ("true", "1", "yes")
        return value
