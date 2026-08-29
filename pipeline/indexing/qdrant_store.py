from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from pipeline.embedding.embedder import LocalEmbedder


COLLECTION_NAME = "regulatoriq"
VECTOR_SIZE = LocalEmbedder.VECTOR_SIZE  # 384


class QdrantStore:
    """
    Stores and searches document chunk vectors in Qdrant.

    What is Qdrant?
      A vector database — a database that stores numbers (vectors) and can
      instantly find the most similar ones for any query vector.
      It runs locally via Docker on port 6333.

    What is stored per chunk?
      - vector: 384 numbers representing the chunk's meaning
      - payload: the original text + all metadata (doc_id, source, date, etc.)

    What can you search for?
      - Semantic search: "RBI rules on cash reserve ratio"
        → finds chunks about CRR even if they use different words
      - Filtered search: same query but only within SEBI documents
        → uses metadata filters on top of vector similarity
    """

    def __init__(self, url: str = "http://localhost:6333"):
        self.client = QdrantClient(url=url)
        self._ensure_collection()

    def _ensure_collection(self):
        """Creates the Qdrant collection if it doesn't exist yet."""
        existing = [c.name for c in self.client.get_collections().collections]
        if COLLECTION_NAME not in existing:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE,  # cosine similarity: best for text
                ),
            )
            logger.info(f"Created Qdrant collection '{COLLECTION_NAME}'")
        else:
            logger.debug(f"Collection '{COLLECTION_NAME}' already exists")

    def upsert(self, embedded_chunks: list[dict]):
        """
        Saves embedded chunks into Qdrant.
        'Upsert' = insert if new, update if already exists (safe to run twice).

        embedded_chunks: output from LocalEmbedder.embed_chunks()
          each item: {"id": str, "vector": list[float], "payload": dict}
        """
        if not embedded_chunks:
            return

        points = []
        for item in embedded_chunks:
            # Qdrant needs integer or UUID ids — we hash the string id to an int
            point_id = abs(hash(item["id"])) % (2**63)
            points.append(
                PointStruct(
                    id=point_id,
                    vector=item["vector"],
                    payload={**item["payload"], "chunk_id": item["id"]},
                )
            )

        self.client.upsert(collection_name=COLLECTION_NAME, points=points)
        logger.info(f"Upserted {len(points)} chunks into Qdrant")

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        regulator: str | None = None,
    ) -> list[dict]:
        """
        Finds the top_k most relevant chunks for a query vector.

        Args:
            query_vector:  output of LocalEmbedder.embed_query()
            top_k:         how many results to return
            regulator:     optional filter — "SEBI" or "RBI" (None = search all)

        Returns:
            List of dicts with keys: text, doc_id, source, score, metadata
        """
        query_filter = None
        if regulator:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="regulator",
                        match=MatchValue(value=regulator),
                    )
                ]
            )

        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )

        return [
            {
                "text": r.payload.get("text", ""),
                "doc_id": r.payload.get("doc_id", ""),
                "source": r.payload.get("source", ""),
                "score": round(r.score, 4),
                "metadata": {k: v for k, v in r.payload.items() if k not in ("text",)},
            }
            for r in results
        ]

    def count(self) -> int:
        """Returns how many chunks are stored in Qdrant."""
        info = self.client.get_collection(COLLECTION_NAME)
        return info.points_count
