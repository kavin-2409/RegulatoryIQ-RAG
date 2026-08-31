from fastapi import APIRouter
from loguru import logger

from backend.models.responses import DocumentsResponse, DocumentSummary
from ingestion.versioning.store import VersionStore

router = APIRouter()


@router.get("/documents", response_model=DocumentsResponse)
async def list_documents():
    """
    Returns a list of all regulatory documents that have been ingested.
    Each entry shows the document ID, latest version number, and when it was last seen.
    """
    logger.info("GET /api/documents")
    store = VersionStore()
    raw = store.get_all_documents()

    docs = [
        DocumentSummary(
            doc_id=d["doc_id"],
            latest_version=d["latest_version"],
            last_seen=d["last_seen"],
        )
        for d in raw
    ]

    return DocumentsResponse(total=len(docs), documents=docs)
