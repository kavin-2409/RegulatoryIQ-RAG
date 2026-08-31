"""
Phase 4 API test — calls the live FastAPI server with HTTP requests.

Start the server first in a separate terminal:
    uvicorn backend.main:app --reload --port 8000

Then run this script:
    python playground/10_test_api.py
"""
import requests

BASE = "http://localhost:8000"


def separator(title: str):
    print(f"\n{'=' * 55}")
    print(f"  {title}")
    print('=' * 55)


# ── 1. Health check ───────────────────────────────────────────
separator("GET /health")
r = requests.get(f"{BASE}/health")
data = r.json()
print(f"Status:           {data['status']}")
print(f"Qdrant running:   {data['qdrant']}")
print(f"Ollama running:   {data['ollama']}")
print(f"Chunks indexed:   {data['documents_indexed']}")

# ── 2. List documents ─────────────────────────────────────────
separator("GET /api/documents")
r = requests.get(f"{BASE}/api/documents")
data = r.json()
print(f"Total documents tracked: {data['total']}")
for doc in data["documents"][:5]:
    print(f"  {doc['doc_id'][:60]}  (v{doc['latest_version']})")
if data["total"] > 5:
    print(f"  ... and {data['total'] - 5} more")

# ── 3. Ask a question ─────────────────────────────────────────
separator("POST /api/ask  (SEBI cybersecurity)")
r = requests.post(f"{BASE}/api/ask", json={
    "question": "What are the SEBI rules on cybersecurity incident reporting?",
    "regulator": "SEBI",
    "top_k": 3,
})
data = r.json()
print(f"Answer:\n{data['answer']}")
print(f"\nConfidence:  {data['confidence']}")
print(f"Grounded:    {data['grounded']}")
print(f"Citations:   {len(data['citations'])}")
for c in data["citations"]:
    print(f"  - {c['source']}  {c['url']}")

# ── 4. Ask another question ───────────────────────────────────
separator("POST /api/ask  (RBI CRR question)")
r = requests.post(f"{BASE}/api/ask", json={
    "question": "What are RBI directions on Cash Reserve Ratio for commercial banks?",
    "regulator": "RBI",
    "top_k": 3,
})
data = r.json()
print(f"Answer:\n{data['answer']}")
print(f"\nConfidence:  {data['confidence']}")
print(f"Grounded:    {data['grounded']}")

# ── 5. Trigger ingest ─────────────────────────────────────────
separator("POST /api/ingest  (RBI, 5 docs)")
r = requests.post(f"{BASE}/api/ingest", json={"source": "rbi", "count": 5})
data = r.json()
print(f"Result: {data['message']}")

print(f"\n{'=' * 55}")
print("All API endpoints working correctly.")
print(f"Interactive docs: {BASE}/docs")
print('=' * 55)
