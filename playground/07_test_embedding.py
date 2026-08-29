import sys
sys.path.insert(0, ".")

from pipeline.chunking.structure_aware import StructureAwareChunker
from pipeline.embedding.embedder import LocalEmbedder

sample_text = """
Reserve Bank of India (Commercial Banks - Cash Reserve Ratio and Statutory
Liquidity Ratio) Fourth Amendment Directions, 2026.

The Reserve Bank of India, having considered it necessary and expedient in the
public interest and in the interest of the banking policy to make the following
amendment to the Reserve Bank of India (Commercial Banks - Cash Reserve Ratio
and Statutory Liquidity Ratio) Directions, 2021.

All Scheduled Commercial Banks shall maintain a Cash Reserve Ratio (CRR) of
4.50 percent of their Net Demand and Time Liabilities (NDTL) as on the last
Friday of the second preceding fortnight.

The Statutory Liquidity Ratio (SLR) shall be maintained at 18 percent of NDTL.
These directions shall come into force with immediate effect.
"""

print("=" * 50)
print("Testing Local Embedder (BAAI/bge-small-en-v1.5)")
print("=" * 50)
print("Note: First run downloads ~133 MB model. This is a one-time download.")
print()

# Step 1: Chunk the text
chunker = StructureAwareChunker(chunk_size=500, overlap=100)
chunks = chunker.chunk("rbi-13680", sample_text, {"source": "RBI Circulars", "regulator": "RBI"})
print(f"Created {len(chunks)} chunks\n")

# Step 2: Embed the chunks
embedder = LocalEmbedder()
embedded = embedder.embed_chunks(chunks)

print(f"\nEmbedded {len(embedded)} chunks")
print(f"Vector size: {len(embedded[0]['vector'])} dimensions")
print()

for item in embedded:
    preview = item["vector"][:5]
    print(f"Chunk ID: {item['id']}")
    print(f"Text:     {item['payload']['text'][:80]}...")
    print(f"Vector:   [{', '.join(f'{v:.4f}' for v in preview)}, ...]  (showing first 5 of 384)")
    print()

# Step 3: Embed a query and show similarity
print("=" * 50)
print("Testing query embedding + similarity")
print("=" * 50)

query = "What is the Cash Reserve Ratio for commercial banks?"
query_vector = embedder.embed_query(query)
print(f"Query: '{query}'")
print(f"Query vector size: {len(query_vector)} dimensions")

# Compute cosine similarity manually (dot product of normalized vectors)
import math

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

print("\nSimilarity scores (1.0 = identical meaning, 0.0 = unrelated):")
for item in embedded:
    score = dot(query_vector, item["vector"])
    print(f"  {score:.4f}  →  {item['payload']['text'][:70]}...")
