import json
import uuid
from typing import Sequence

from pgvector.sqlalchemy import Vector
from sqlalchemy import select, Text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk
from app.settings.config import get_settings
from app.services.settings_service import SettingsService

settings = get_settings()


class RAGService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self._settings_service = SettingsService(db)
        self._embedder = None

    async def _get_embedder(self):
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                model_name = settings.EMBEDDING_MODEL
                self._embedder = SentenceTransformer(model_name)
            except ImportError:
                raise RuntimeError(
                    "sentence-transformers not installed. "
                    "Run: pip install sentence-transformers"
                )
        return self._embedder

    async def _embed(self, texts: list[str]) -> list[list[float]]:
        embedder = await self._get_embedder()
        embeddings = embedder.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def _chunk_text(self, text: str, filename: str) -> list[dict]:
        from app.services.settings_service import SettingsService

        chunk_size = settings.RAG_CHUNK_SIZE
        chunk_overlap = settings.RAG_CHUNK_OVERLAP

        chunks = []
        start = 0
        index = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append({
                "filename": filename,
                "chunk_index": index,
                "content": text[start:end],
            })
            index += 1
            start += chunk_size - chunk_overlap
            if start >= len(text):
                break

        return chunks

    async def ingest_text(self, filename: str, text: str) -> list[DocumentChunk]:
        raw_chunks = self._chunk_text(text, filename)
        contents = [c["content"] for c in raw_chunks]

        embeddings = await self._embed(contents)

        db_chunks = []
        for rc, emb in zip(raw_chunks, embeddings):
            chunk = DocumentChunk(
                filename=rc["filename"],
                chunk_index=rc["chunk_index"],
                content=rc["content"],
                embedding=emb,
                metadata_json=json.dumps({"filename": filename, "source": "upload"}),
            )
            self.db.add(chunk)
            db_chunks.append(chunk)

        await self.db.flush()
        return db_chunks

    async def retrieve(self, query: str, top_k: int | None = None) -> Sequence[DocumentChunk]:
        if top_k is None:
            top_k_val = await self._settings_service.get_typed_value("rag_top_k")
            top_k = int(top_k_val) if top_k_val is not None else settings.RAG_TOP_K

        query_embedding = (await self._embed([query]))[0]
        embedding_col = DocumentChunk.embedding

        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.embedding.isnot(None))
            .order_by(embedding_col.cosine_distance(query_embedding))
            .limit(top_k)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_document(self, chunk_id: uuid.UUID) -> bool:
        chunk = await self.db.get(DocumentChunk, chunk_id)
        if chunk:
            await self.db.delete(chunk)
            return True
        return False
