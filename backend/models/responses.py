from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str          # "ok" or "degraded"
    qdrant: bool         # True if Qdrant is reachable
    ollama: bool         # True if Ollama is reachable
    documents_indexed: int  # total chunks in Qdrant


class DocumentSummary(BaseModel):
    doc_id: str
    latest_version: int
    last_seen: str       # ISO timestamp


class DocumentsResponse(BaseModel):
    total: int
    documents: list[DocumentSummary]


class IngestResponse(BaseModel):
    ingested: int        # number of new/changed documents saved
    message: str
