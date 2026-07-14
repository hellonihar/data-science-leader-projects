import uuid
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.document import DocumentChunk
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.filename is None:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()
    text = content.decode("utf-8", errors="replace")

    rag_service = RAGService(db)
    chunks = await rag_service.ingest_text(file.filename, text)

    return {
        "filename": file.filename,
        "chunks_count": len(chunks),
        "message": f"Indexed {len(chunks)} chunks from {file.filename}",
    }


@router.get("")
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DocumentChunk.filename, DocumentChunk.metadata_json)
        .distinct(DocumentChunk.filename)
        .order_by(DocumentChunk.filename, DocumentChunk.created_at.desc())
    )
    files = {}
    for filename, metadata_json in result:
        if filename not in files:
            meta = json.loads(metadata_json) if metadata_json else {}
            files[filename] = meta

    return [
        {"filename": f, "metadata": meta} for f, meta in files.items()
    ]


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    chunk = await db.get(DocumentChunk, document_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Document chunk not found")
    await db.delete(chunk)
