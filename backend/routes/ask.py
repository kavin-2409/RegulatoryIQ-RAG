from fastapi import APIRouter, HTTPException
from loguru import logger

from backend.models.requests import AskRequest
from generation.schemas import RegulatoryAnswer
from generation.generator import RAGGenerator

router = APIRouter()

# One shared generator instance — the embedding model loads once and stays in memory
_generator: RAGGenerator | None = None


def get_generator() -> RAGGenerator:
    global _generator
    if _generator is None:
        _generator = RAGGenerator()
    return _generator


@router.post("/ask", response_model=RegulatoryAnswer)
async def ask(body: AskRequest):
    """
    Ask a question about Indian financial regulations.

    The system retrieves the most relevant chunks from SEBI/RBI documents
    stored in Qdrant, then uses phi3 (local LLM) to generate a grounded answer.

    Returns a structured answer with citations, confidence score, and a
    grounding flag that indicates whether the answer is supported by the
    retrieved documents.
    """
    logger.info(f"POST /api/ask  question={body.question!r}  regulator={body.regulator}")

    try:
        gen = get_generator()
        answer = gen.ask(body.question, regulator=body.regulator)
        return answer
    except RuntimeError as e:
        # Ollama or Qdrant not running
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /ask: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
