"""
Full Phase 2 pipeline test:
  Scrape  →  Chunk  →  Embed  →  Store in Qdrant  →  Search

Requires Qdrant running: docker-compose up -d
"""
import sys
sys.path.insert(0, ".")

from ingestion.scrapers.sebi import SEBIScraper
from ingestion.scrapers.rbi import RBIScraper
from ingestion.versioning.hasher import hash_document
from ingestion.versioning.store import VersionStore
from pipeline.chunking.structure_aware import StructureAwareChunker
from pipeline.embedding.embedder import LocalEmbedder
from pipeline.indexing.qdrant_store import QdrantStore

print("=" * 55)
print("PHASE 2: Full Pipeline Test")
print("Scrape → Chunk → Embed → Index → Search")
print("=" * 55)

# ── Step 1: Scrape ────────────────────────────────────────────
print("\nSTEP 1: Scraping documents")
print("-" * 40)

all_docs = []
sebi = SEBIScraper(category="circulars")
sebi_docs = sebi.fetch_documents(count=10)
print(f"SEBI: {len(sebi_docs)} documents")
all_docs.extend(sebi_docs)

rbi = RBIScraper()
rbi_docs = rbi.fetch_documents(count=15)
print(f"RBI:  {len(rbi_docs)} documents")
all_docs.extend(rbi_docs)

print(f"Total: {len(all_docs)} documents")

# ── Step 2: Chunk ─────────────────────────────────────────────
print("\nSTEP 2: Chunking documents")
print("-" * 40)

chunker = StructureAwareChunker(chunk_size=1000, overlap=150)
all_chunks = []

for doc in all_docs:
    chunks = chunker.chunk(doc.id, doc.content, {
        "source": doc.source,
        "title": doc.title,
        "url": doc.url,
        "published_date": doc.published_date,
        **doc.metadata,
    })
    all_chunks.extend(chunks)
    print(f"  {doc.id[:50]}  →  {len(chunks)} chunks")

print(f"\nTotal chunks: {len(all_chunks)}")

# ── Step 3: Embed ─────────────────────────────────────────────
print("\nSTEP 3: Embedding chunks (first run downloads ~133 MB model)")
print("-" * 40)

embedder = LocalEmbedder()
embedded = embedder.embed_chunks(all_chunks)
print(f"Embedded {len(embedded)} chunks  ({embedded[0]['vector'].__len__()} dimensions each)")

# ── Step 4: Store in Qdrant ───────────────────────────────────
print("\nSTEP 4: Storing in Qdrant")
print("-" * 40)
print("(Qdrant must be running: docker-compose up -d)")

store = QdrantStore()
store.upsert(embedded)
print(f"Qdrant now holds {store.count()} chunks total")

# ── Step 5: Search ────────────────────────────────────────────
print("\nSTEP 5: Semantic Search Demo")
print("-" * 40)

queries = [
    "SEBI circular on cybersecurity incident reporting",
    "RBI cash reserve ratio for commercial banks",
    "ETF price bands and pre-open session rules",
]

for query in queries:
    print(f"\nQuery: '{query}'")
    query_vector = embedder.embed_query(query)
    results = store.search(query_vector, top_k=2)
    for i, r in enumerate(results, 1):
        print(f"  [{i}] score={r['score']}  source={r['source']}")
        print(f"       {r['text'][:120]}...")

print("\n" + "=" * 55)
print("Phase 2 complete! Documents are now searchable by meaning.")
print("Phase 3 will add the LLM to generate answers from these results.")
print("=" * 55)
