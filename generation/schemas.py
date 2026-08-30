from pydantic import BaseModel


class Citation(BaseModel):
    """One source document that supports the answer."""
    doc_id: str
    source: str       # e.g. "SEBI Circulars", "RBI Circulars"
    excerpt: str      # the relevant sentence from the chunk
    url: str


class RegulatoryAnswer(BaseModel):
    """
    The structured output returned for every question.

    Having a fixed structure means:
    - The frontend always knows what fields to display
    - We can run automated quality checks on every field
    - Hiring managers see you designed an API-first system
    """
    question: str
    answer: str              # the generated answer in plain English
    citations: list[Citation]  # which documents support the answer
    confidence: str          # "high" | "medium" | "low"
    grounded: bool           # True if guardrail passed (answer is in the docs)
    retrieved_chunks: int    # how many chunks were used as context
