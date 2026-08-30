SYSTEM_PROMPT = """You are RegulatorIQ, an AI assistant specializing in Indian financial regulations from SEBI and RBI.

Your rules:
1. Answer ONLY using the provided regulatory documents below.
2. Always cite which document number [1], [2], etc. supports each claim.
3. If the documents do not contain enough information, say exactly: "The provided documents do not contain sufficient information to answer this question."
4. Never make up rules, dates, percentages, or regulatory requirements.
5. Be concise and factual. Write for a compliance professional."""


def build_user_prompt(question: str, chunks: list[dict]) -> str:
    """
    Assembles the context (retrieved chunks) + question into a single prompt.
    Each chunk is numbered [1], [2], etc. so the model can cite them.
    """
    lines = ["REGULATORY DOCUMENTS:"]
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "Unknown")
        date = chunk.get("metadata", {}).get("published_date", "")
        url = chunk.get("metadata", {}).get("url", "")
        lines.append(f"\n[{i}] {source} | {date}")
        if url:
            lines.append(f"    URL: {url}")
        # Cap each chunk at 600 chars to keep prompt within phi3's context window
    lines.append(f"    {chunk['text'][:600]}")

    lines.append(f"\nQUESTION: {question}")
    lines.append("\nANSWER (cite document numbers in square brackets):")

    return "\n".join(lines)
