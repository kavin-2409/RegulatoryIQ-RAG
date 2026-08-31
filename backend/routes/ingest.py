from fastapi import APIRouter, HTTPException
from loguru import logger

from backend.models.requests import IngestRequest
from backend.models.responses import IngestResponse
from ingestion.scrapers.sebi import SEBIScraper
from ingestion.scrapers.rbi import RBIScraper
from ingestion.versioning.hasher import hash_document, has_changed
from ingestion.versioning.store import VersionStore
from pipeline.chunking.structure_aware import StructureAwareChunker
from pipeline.embedding.embedder import LocalEmbedder
from pipeline.indexing.qdrant_store import QdrantStore

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(body: IngestRequest):
    """
    Triggers a fresh scrape from SEBI and/or RBI, then chunks, embeds,
    and indexes any new or changed documents into Qdrant.

    This is the pipeline that keeps RegulatorIQ up to date with the
    latest circulars without any manual work.
    """
    logger.info(f"POST /api/ingest  source={body.source}  count={body.count}")

    try:
        # ── Scrape ────────────────────────────────────────────────────────
        docs = []
        if body.source in ("sebi", "all"):
            sebi = SEBIScraper(category="circulars")
            docs.extend(sebi.fetch_documents(count=body.count))

        if body.source in ("rbi", "all"):
            rbi = RBIScraper()
            docs.extend(rbi.fetch_documents(count=body.count))

        # ── Version check ─────────────────────────────────────────────────
        store = VersionStore()
        chunker = StructureAwareChunker()
        embedder = LocalEmbedder()
        qdrant = QdrantStore()

        new_count = 0
        for doc in docs:
            doc_hash = hash_document(doc.content)
            if not has_changed(doc.id, doc_hash, store):
                continue  # already indexed, skip

            store.save_version(doc.id, doc_hash, doc.content, doc.metadata)

            chunks = chunker.chunk(doc.id, doc.content, {
                "source": doc.source,
                "title": doc.title,
                "url": doc.url,
                "published_date": doc.published_date,
                **doc.metadata,
            })

            if chunks:
                embedded = embedder.embed_chunks(chunks)
                qdrant.upsert(embedded)

            new_count += 1

        msg = (
            f"Ingested {new_count} new/changed documents from {body.source.upper()}."
            if new_count > 0
            else f"No new documents found. All {len(docs)} documents are already up to date."
        )
        logger.info(msg)
        return IngestResponse(ingested=new_count, message=msg)

    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
