from loguru import logger
from pipeline.chunking.structure_aware import Chunk


class LocalEmbedder:
    """
    Converts text chunks into vectors (lists of numbers) using a free
    local model — no API key, no cost, runs entirely on your machine.

    Model: BAAI/bge-small-en-v1.5
      - Downloaded once (~133 MB) and cached locally
      - Produces 384-dimensional vectors
      - Good quality for English regulatory text
      - Runs on CPU (no GPU needed)

    What is an embedding / vector?
      Text like "SEBI circular on ETF pricing" becomes a list of 384 numbers,
      e.g. [0.12, -0.45, 0.87, ...].  Two texts that mean similar things
      produce vectors that are "close" to each other in 384-dimensional space.
      Qdrant uses this to find the most relevant chunks for any question.
    """

    MODEL_NAME = "BAAI/bge-small-en-v1.5"
    VECTOR_SIZE = 384

    def __init__(self):
        self._model = None  # loaded lazily on first use

    def _load(self):
        if self._model is None:
            logger.info(f"Loading embedding model '{self.MODEL_NAME}' (first run downloads ~133 MB)...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.MODEL_NAME)
            logger.info("Embedding model ready.")

    def embed_chunks(self, chunks: list[Chunk]) -> list[dict]:
        """
        Embeds a list of Chunk objects.

        Returns a list of dicts, one per chunk:
          {
            "id":       chunk id string,
            "vector":   list of 384 floats,
            "payload":  everything needed to reconstruct the result (text + metadata)
          }
        """
        if not chunks:
            return []

        self._load()

        texts = [chunk.text for chunk in chunks]
        logger.info(f"Embedding {len(texts)} chunks...")

        # encode() returns a numpy array; tolist() converts to plain Python lists
        vectors = self._model.encode(
            texts,
            batch_size=32,
            show_progress_bar=len(texts) > 10,
            normalize_embeddings=True,  # cosine similarity works best with normalized vectors
        )

        results = []
        for chunk, vector in zip(chunks, vectors):
            results.append({
                "id": chunk.id,
                "vector": vector.tolist(),
                "payload": {
                    "doc_id": chunk.doc_id,
                    "text": chunk.text,
                    "chunk_index": chunk.chunk_index,
                    **chunk.metadata,
                },
            })

        logger.info(f"Embedded {len(results)} chunks successfully.")
        return results

    def embed_query(self, query: str) -> list[float]:
        """
        Embeds a single search query string.
        Used at search time to find relevant chunks.
        """
        self._load()
        vector = self._model.encode(
            query,
            normalize_embeddings=True,
        )
        return vector.tolist()
