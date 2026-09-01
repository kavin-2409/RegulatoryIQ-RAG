"""
Local evaluation metrics — no external LLM or API required.

Faithfulness   : fraction of answer tokens that appear in retrieved chunks
Answer relevance: fraction of question keywords found in the answer
Context precision: fraction of retrieved chunks that contain ≥1 question keyword
"""

import re


def _tokenize(text: str) -> set[str]:
    """Lowercase alphanumeric tokens, min length 3."""
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) >= 3}


def faithfulness(answer: str, chunks: list[dict]) -> float:
    """
    What fraction of meaningful answer words appear in the retrieved context?
    Range: 0.0 – 1.0  (higher = more grounded in sources)
    """
    if not answer or not chunks:
        return 0.0

    # Combine all chunk text
    context = " ".join(c.get("text", c.get("payload", {}).get("text", "")) for c in chunks)
    context_tokens = _tokenize(context)
    answer_tokens = _tokenize(answer)

    if not answer_tokens:
        return 0.0

    overlap = answer_tokens & context_tokens
    return round(len(overlap) / len(answer_tokens), 3)


def answer_relevance(question: str, answer: str) -> float:
    """
    What fraction of question keywords appear in the answer?
    Range: 0.0 – 1.0  (higher = answer addresses the question)
    """
    if not question or not answer:
        return 0.0

    q_tokens = _tokenize(question)
    a_tokens = _tokenize(answer)

    if not q_tokens:
        return 0.0

    overlap = q_tokens & a_tokens
    return round(len(overlap) / len(q_tokens), 3)


def context_precision(question: str, chunks: list[dict]) -> float:
    """
    Fraction of retrieved chunks that contain at least one question keyword.
    Range: 0.0 – 1.0  (higher = retrieval was on-topic)
    """
    if not chunks or not question:
        return 0.0

    q_tokens = _tokenize(question)
    if not q_tokens:
        return 0.0

    relevant = 0
    for c in chunks:
        chunk_text = c.get("text", c.get("payload", {}).get("text", ""))
        chunk_tokens = _tokenize(chunk_text)
        if q_tokens & chunk_tokens:
            relevant += 1

    return round(relevant / len(chunks), 3)


def reference_coverage(answer: str, reference_terms: list[str]) -> float:
    """
    Fraction of reference key-terms (from the eval dataset) found in the answer.
    Acts as a proxy for recall against a known-correct answer.
    Range: 0.0 – 1.0
    """
    if not answer or not reference_terms:
        return 0.0

    answer_lower = answer.lower()
    found = sum(1 for term in reference_terms if term.lower() in answer_lower)
    return round(found / len(reference_terms), 3)


def overall_score(faithfulness_s: float, answer_relevance_s: float,
                  context_precision_s: float, reference_coverage_s: float) -> float:
    """Weighted average of the four metrics."""
    weights = [0.35, 0.25, 0.20, 0.20]
    scores = [faithfulness_s, answer_relevance_s, context_precision_s, reference_coverage_s]
    return round(sum(w * s for w, s in zip(weights, scores)), 3)
