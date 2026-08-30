import requests
from loguru import logger

from pipeline.embedding.embedder import LocalEmbedder
from pipeline.indexing.qdrant_store import QdrantStore
from generation.schemas import RegulatoryAnswer, Citation
from generation.prompts.templates import SYSTEM_PROMPT, build_user_prompt
from generation.guardrails import is_grounded, score_confidence


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "phi3:latest"


class RAGGenerator:
    """
    The core of RegulatorIQ — ties together retrieval and generation.

    Flow for every question:
      1. Embed the question (convert to vector)
      2. Search Qdrant for the top-k most relevant chunks
      3. Build a prompt: system instructions + retrieved chunks + question
      4. Send to Ollama (phi3 running locally) and get an answer
      5. Run guardrails (is the answer grounded in the documents?)
      6. Return a structured RegulatoryAnswer with citations

    This is the RAG loop: Retrieve → Augment → Generate
    """

    def __init__(
        self,
        top_k: int = 5,
        ollama_url: str = OLLAMA_URL,
        model: str = OLLAMA_MODEL,
    ):
        self.top_k = top_k
        self.ollama_url = ollama_url
        self.model = model
        self.embedder = LocalEmbedder()
        self.store = QdrantStore()

    def ask(self, question: str, regulator: str | None = None) -> RegulatoryAnswer:
        """
        Ask a question about Indian financial regulations.

        Args:
            question:   plain English question, e.g. "What is the CRR for commercial banks?"
            regulator:  optional filter — "SEBI", "RBI", or None (search all)

        Returns:
            RegulatoryAnswer with answer, citations, confidence, and grounding check
        """
        logger.info(f"Question: {question}")

        # ── Step 1: Retrieve ──────────────────────────────────────────────
        query_vector = self.embedder.embed_query(question)
        chunks = self.store.search(query_vector, top_k=self.top_k, regulator=regulator)

        if not chunks:
            return RegulatoryAnswer(
                question=question,
                answer="No relevant documents found in the database. Please run the ingestion pipeline first.",
                citations=[],
                confidence="low",
                grounded=False,
                retrieved_chunks=0,
            )

        logger.info(f"Retrieved {len(chunks)} chunks from Qdrant")

        # ── Step 2: Augment ───────────────────────────────────────────────
        user_prompt = build_user_prompt(question, chunks)

        # ── Step 3: Generate ──────────────────────────────────────────────
        answer_text = self._call_ollama(user_prompt)
        logger.info("Answer generated")

        # ── Step 4: Guardrails ────────────────────────────────────────────
        grounded = is_grounded(answer_text, chunks)
        confidence = score_confidence(answer_text, chunks)

        if not grounded:
            logger.warning("Guardrail: answer may contain information not in retrieved chunks")

        # ── Step 5: Build citations ───────────────────────────────────────
        citations = self._build_citations(chunks)

        return RegulatoryAnswer(
            question=question,
            answer=answer_text,
            citations=citations,
            confidence=confidence,
            grounded=grounded,
            retrieved_chunks=len(chunks),
        )

    def _call_ollama(self, user_prompt: str) -> str:
        """Sends the prompt to Ollama and returns the response text."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,   # low temperature = factual, less creative
                "num_predict": 400,   # max tokens in the answer
                "num_ctx": 4096,      # context window size for phi3
            },
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            if not response.ok:
                logger.error(f"Ollama error {response.status_code}: {response.text[:500]}")
            response.raise_for_status()
            return response.json()["message"]["content"].strip()
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Cannot reach Ollama. Make sure it is running: open a terminal and run 'ollama serve'"
            )
        except Exception as e:
            raise RuntimeError(f"Ollama call failed: {e}")

    def _build_citations(self, chunks: list[dict]) -> list[Citation]:
        """Builds citation objects from the retrieved chunks."""
        seen_docs = set()
        citations = []

        for chunk in chunks:
            doc_id = chunk.get("doc_id", "")
            if doc_id in seen_docs:
                continue  # one citation per document, not per chunk
            seen_docs.add(doc_id)

            citations.append(Citation(
                doc_id=doc_id,
                source=chunk.get("source", ""),
                excerpt=chunk.get("text", "")[:200] + "...",
                url=chunk.get("metadata", {}).get("url", ""),
            ))

        return citations
