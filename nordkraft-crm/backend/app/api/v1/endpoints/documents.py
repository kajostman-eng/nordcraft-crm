from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Document, User
from app.schemas.schemas import DocumentOut
from app.services.storage_service import upload_fileobj


router = APIRouter()


@router.get("/", response_model=List[DocumentOut])
async def list_documents(
    lead_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Document).order_by(Document.created_at.desc())
    if lead_id:
        q = q.where(Document.lead_id == lead_id)
    if client_id:
        q = q.where(Document.client_id == client_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(None),
    lead_id: str | None = Form(None),
    client_id: str | None = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    ext = os.path.splitext(file.filename)[1].lower()
    safe_ext = ext if len(ext) <= 12 else ""
    storage_key = f"documents/{datetime.utcnow().strftime('%Y/%m/%d')}/{user.id}/{datetime.utcnow().timestamp():.0f}{safe_ext}"

    url = upload_fileobj(fileobj=file.file, key=storage_key, content_type=file.content_type)

    doc = Document(
        title=title,
        description=description,
        file_name=file.filename,
        content_type=file.content_type,
        size_bytes=None,
        storage_key=storage_key,
        url=url or None,
        lead_id=lead_id,
        client_id=client_id,
        uploaded_by=user.id,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    await db.delete(doc)
    await db.commit()

