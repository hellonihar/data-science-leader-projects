import json
from time import time

from groq import AsyncGroq
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk
from app.settings.config import get_settings
from app.services.settings_service import SettingsService

settings = get_settings()

BASELINE_SYSTEM_PROMPT = """You are a helpful clinical assistant. Answer the user's question to the best of your ability based on your training. If you are unsure of an answer, say so clearly. Do not fabricate medical information."""

RAG_SYSTEM_PROMPT = """You are a clinical decision support assistant. Use the provided clinical document excerpts to answer the user's question. If the documents do not contain sufficient information to answer, say so clearly. Cite specific passages when possible. Do not fabricate information not present in the provided context."""


class LLMService:

    def __init__(self, db: AsyncSession, redis: Redis):
        self.db = db
        self.redis = redis
        self._client: AsyncGroq | None = None
        self._settings_service = SettingsService(db)

    @property
    async def client(self) -> AsyncGroq:
        if self._client is None:
            self._client = AsyncGroq(
                api_key=settings.GROQ_API_KEY,
                base_url=settings.GROQ_BASE_URL,
            )
        return self._client

    async def _get_param(self, key: str, default: str) -> str:
        val = await self._settings_service.get_typed_value(key)
        return str(val) if val is not None else default

    async def _build_prompt(self, system_prompt: str, query: str, chunks: list[DocumentChunk] | None = None) -> list[dict]:
        messages = [{"role": "system", "content": system_prompt}]

        if chunks:
            context_parts = []
            for i, chunk in enumerate(chunks):
                context_parts.append(f"[Source {i + 1}]: {chunk.content}")
            context = "\n\n".join(context_parts)
            messages.append({
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}",
            })
        else:
            messages.append({"role": "user", "content": query})

        return messages

    async def generate_baseline(self, query: str) -> str:
        model = await self._get_param("groq_model_baseline", settings.GROQ_MODEL_BASELINE)
        temperature = float(await self._get_param("groq_temperature", str(settings.GROQ_TEMPERATURE)))
        max_tokens = int(await self._get_param("groq_max_tokens", str(settings.GROQ_MAX_TOKENS)))

        messages = await self._build_prompt(BASELINE_SYSTEM_PROMPT, query)

        groq_client = await self.client
        response = await groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def generate_with_rag(self, query: str, chunks: list[DocumentChunk]) -> str:
        model = await self._get_param("groq_model_finetuned", settings.GROQ_MODEL_FINETUNED)
        temperature = float(await self._get_param("groq_temperature", str(settings.GROQ_TEMPERATURE)))
        max_tokens = int(await self._get_param("groq_max_tokens", str(settings.GROQ_MAX_TOKENS)))

        messages = await self._build_prompt(RAG_SYSTEM_PROMPT, query, chunks)

        groq_client = await self.client
        response = await groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
