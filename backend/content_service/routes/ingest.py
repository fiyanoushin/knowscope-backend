"""
routes/ingest.py
================
PDF textbook ingestion pipeline.

Teacher/Admin workflow:
  POST /ingest/pdf          — Upload PDF with metadata → extract, clean, chunk, embed, store
  DELETE /ingest/book/{id}  — Wipe all data for a book (MongoDB + ChromaDB)
  GET  /ingest/books        — List all book IDs stored in MongoDB
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import tempfile
from app.database import raw_pages_collection, chapters_collection, topics_collection, chunks_collection
from services.pdf_loader import extract_pages
from services.chapter_pipeline import build_chapters
from services.topic_extractor import build_topics
from services.chunk_builder import build_chunks
from app.vector_store import vector_store
from fastapi import APIRouter, UploadFile, File, Form,Header,Depends
from .jwt_utils import get_current_user_from_header ,require_admin

router = APIRouter(prefix="/vectordb", tags=["vectordb"])


# ─────────────────────────────────────────────
# POST /ingest/pdf
# ─────────────────────────────────────────────

@router.post("/storpdf_forembedding")
async def ingest_pdf(
    file: UploadFile = File(...),
    # book_id: str = Form(...),
    class_number: int = Form(...),
    subject: str = Form(...),
    # current_admin: dict = Depends(require_admin)
):
    last_doc = await raw_pages_collection.find_one({},sort=[("book_id", -1)])

    if last_doc:
        book_id=last_doc["book_id"] + 1
    else:
        book_id=0
    existing = await raw_pages_collection.find_one({"book_id": book_id})
    if existing:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Book '{book_id}' is already ingested. "
                f"To re-ingest, first DELETE /ingest/book/{book_id} then upload again."
            )
        )

    # ── Save PDF to temp file ────────────────────────────────────────────────
    suffix = os.path.splitext(file.filename or "upload.pdf")[1] or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # ── Step 1: Extract pages ────────────────────────────────────────────
        pages = extract_pages(tmp_path)
        if not pages:
            raise HTTPException(
                status_code=422,
                detail="No readable text found in the uploaded PDF."
            )

        # Attach book metadata to each page
        for page in pages:
            page["book_id"] = book_id
            page["class"] = class_number
            page["subject"] = subject.strip().lower()

        # ── Step 2: Store raw pages in MongoDB ───────────────────────────────
        await raw_pages_collection.insert_many(pages)

        # ── Step 3: Build chapters ───────────────────────────────────────────
        chapters = await build_chapters(book_id)

        # ── Step 4: Build topics ─────────────────────────────────────────────
        await build_topics(book_id)

        # ── Step 5: Build chunks + embeddings → ChromaDB ─────────────────────
        total_chunks = await build_chunks(book_id, class_number, subject.strip().lower())

    finally:
        os.unlink(tmp_path)

    return {
        "message": "✅ PDF ingested successfully",
        "book_id": book_id,
        "class": class_number,
        "subject": subject,
        "pages_extracted": len(pages),
        "chapters_created": len(chapters),
        "total_chunks_indexed": total_chunks,
        # "uploaded_by": current_admin["user_id"]
        
    }


# ─────────────────────────────────────────────
# DELETE /ingest/book/{book_id}
# ─────────────────────────────────────────────

@router.delete("/book/{book_id}")
async def delete_book(book_id: str):
    """
    Completely remove a book from the system:
    - Deletes raw_pages, chapters, topics, and chunks from MongoDB
    - Deletes all vector embeddings from ChromaDB
    """
    # Delete from MongoDB collections
    r1 = await raw_pages_collection.delete_many({"book_id": book_id})
    r2 = await chapters_collection.delete_many({"book_id": book_id})
    r3 = await topics_collection.delete_many({"book_id": book_id})
    r4 = await chunks_collection.delete_many({"book_id": book_id})

    # Delete from ChromaDB vector store
    await vector_store.delete_book_chunks(book_id)

    return {
        "message": f"✅ Book '{book_id}' deleted from all stores",
        "deleted": {
            "raw_pages": r1.deleted_count,
            "chapters": r2.deleted_count,
            "topics": r3.deleted_count,
            "chunks": r4.deleted_count,
            "vector_chunks": "all"
        }
    }


# ─────────────────────────────────────────────
# GET /ingest/books
# ─────────────────────────────────────────────

@router.get("/books")
async def list_ingested_books():
    """
    List all book IDs that have been ingested into the system.
    """
    book_ids = await raw_pages_collection.distinct("book_id")
    return {
        "total": len(book_ids),
        "books": book_ids
    }