"""
Hallucination guardrail.

The biggest risk in RAG systems is the LLM making up information that is not
in the retrieved documents. This module checks whether the answer is grounded
in (supported by) the retrieved chunks.

How it works:
  1. Extract meaningful words from the answer (filter out stop words)
  2. Check how many of those words appear in the retrieved chunks
  3. If the overlap is below a threshold, the answer is likely hallucinated

This is a lightweight keyword-overlap approach. A production system would
use a second LLM call ("does the evidence support the claim?") but for a
portfolio project this catches the most obvious hallucinations.
"""

import re

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "to", "of", "in", "on", "at", "by",
    "for", "with", "about", "from", "into", "that", "this", "these", "those",
    "it", "its", "and", "or", "but", "not", "as", "if", "then", "than",
    "so", "also", "all", "any", "each", "which", "who", "what", "when",
    "how", "i", "we", "you", "they", "he", "she", "per", "based", "provided",
}


def _extract_keywords(text: str) -> set[str]:
    """Lowercased words longer than 3 chars that are not stop words."""
    words = re.findall(r"[a-zA-Z]{4,}", text.lower())
    return {w for w in words if w not in STOP_WORDS}


def is_grounded(answer: str, chunks: list[dict], threshold: float = 0.35) -> bool:
    """
    Returns True if at least `threshold` fraction of the answer's keywords
    appear somewhere in the retrieved chunks.

    Args:
        answer:     the LLM-generated answer text
        chunks:     the retrieved chunks used as context (list of dicts with 'text')
        threshold:  minimum keyword overlap ratio (default 35%)

    Returns:
        True  → answer appears grounded in the provided documents
        False → answer may contain hallucinated information
    """
    # If the model correctly said it couldn't find the answer, it's grounded
    no_info_phrase = "do not contain sufficient information"
    if no_info_phrase in answer.lower():
        return True

    answer_keywords = _extract_keywords(answer)
    if not answer_keywords:
        return True  # nothing to check

    # Combine all chunk text into one big string for keyword lookup
    all_chunk_text = " ".join(c.get("text", "") for c in chunks).lower()

    matched = sum(1 for kw in answer_keywords if kw in all_chunk_text)
    overlap_ratio = matched / len(answer_keywords)

    return overlap_ratio >= threshold


def score_confidence(answer: str, chunks: list[dict]) -> str:
    """
    Returns "high", "medium", or "low" based on keyword overlap with chunks.
    Used to show the user how reliable the answer is.
    """
    if "do not contain sufficient information" in answer.lower():
        return "low"

    answer_keywords = _extract_keywords(answer)
    if not answer_keywords:
        return "low"

    all_chunk_text = " ".join(c.get("text", "") for c in chunks).lower()
    matched = sum(1 for kw in answer_keywords if kw in all_chunk_text)
    ratio = matched / len(answer_keywords)

    if ratio >= 0.6:
        return "high"
    elif ratio >= 0.35:
        return "medium"
    else:
        return "low"
