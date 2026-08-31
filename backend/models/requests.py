from pydantic import BaseModel, Field
from typing import Literal


class AskRequest(BaseModel):
    """Body sent by the frontend when asking a question."""
    question: str = Field(..., min_length=5, max_length=500)
    regulator: Literal["SEBI", "RBI"] | None = Field(
        default=None,
        description="Filter results to a specific regulator. None = search all.",
    )
    top_k: int = Field(default=3, ge=1, le=10)


class IngestRequest(BaseModel):
    """Body sent to trigger a fresh scrape and re-index."""
    source: Literal["sebi", "rbi", "all"] = "all"
    count: int = Field(default=10, ge=1, le=50)
