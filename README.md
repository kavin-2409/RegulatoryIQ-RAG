# RegulatorIQ

**AI-powered Q&A system for Indian financial regulations — SEBI + RBI.**

Ask plain-English questions about SEBI circulars and RBI directions and get structured answers with citations, confidence scores, and grounding checks — all running **100% locally**, no paid API required.

> Built as a portfolio project to demonstrate end-to-end RAG (Retrieval-Augmented Generation) engineering.

---

## Demo

| Ask a question | Get a cited, grounded answer |
|---|---|
| "What are SEBI's cybersecurity requirements for stock brokers?" | Answer + source circulars + confidence badge + grounded/ungrounded flag |
| "What is the CRR requirement set by RBI?" | Answer with citations linking back to actual RBI circulars |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INGESTION PIPELINE                        │
│                                                                   │
│  SEBI Website ──┐                                                 │
│                  ├──► BeautifulSoup Scrapers                      │
│  RBI Website  ──┘         │                                       │
│                            ▼                                      │
│                   Structure-Aware Chunker                         │
│                   (paragraph → sentence → merge, overlap=150)     │
│                            │                                      │
│                            ▼                                      │
│                   BAAI/bge-small-en-v1.5                          │
│                   (384-dim embeddings, local, free)               │
│                            │                                      │
│                            ▼                                      │
│                        Qdrant DB  ◄──── SHA-256 versioning        │
│                        (port 6333)      (SQLite, dedup)           │
└─────────────────────────────────────────────────────────────────┘
                              │
                      Vector search
                              │
┌─────────────────────────────────────────────────────────────────┐
│                         QUERY PIPELINE                           │
│                                                                   │
│  User question                                                    │
│       │                                                           │
│       ▼                                                           │
│  Embed query (bge-small-en-v1.5)                                  │
│       │                                                           │
│       ▼                                                           │
│  Qdrant search → top-5 chunks (filtered by SEBI/RBI)             │
│       │                                                           │
│       ▼                                                           │
│  Build prompt (system + numbered chunks + question)               │
│       │                                                           │
│       ▼                                                           │
│  phi3:latest via Ollama  (local, free, temperature=0.1)          │
│       │                                                           │
│       ▼                                                           │
│  Guardrails: keyword overlap check (≥35% → grounded)             │
│       │                                                           │
│       ▼                                                           │
│  RegulatoryAnswer { answer, citations, confidence, grounded }     │
└─────────────────────────────────────────────────────────────────┘
                              │
                         FastAPI (port 8000)
                              │
                    React + Vite + Tailwind (port 3000)
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Scraping** | BeautifulSoup4 + requests | Parses SEBI/RBI HTML tables |
| **Chunking** | Custom structure-aware splitter | Preserves paragraph boundaries, 1000-char chunks with 150-char overlap |
| **Embeddings** | `BAAI/bge-small-en-v1.5` | Free, CPU-friendly, 384-dim, ~133 MB one-time download |
| **Vector DB** | Qdrant (Docker) | Local, production-grade, filtered search by regulator |
| **Versioning** | SHA-256 + SQLite | Deduplicates documents across ingestion runs |
| **LLM** | `phi3:latest` via Ollama | Free, runs locally, 2.2 GB, no GPU needed |
| **Backend** | FastAPI + Pydantic | REST API with typed request/response models |
| **Frontend** | React 18 + Vite + Tailwind CSS | Chat UI with source filter and live system-status panel |
| **Evaluation** | Custom metrics (no OpenAI) | Faithfulness, answer relevance, context precision, reference coverage |
| **CI** | GitHub Actions | Lightweight CI on every push (no heavy ML deps) |

---

## Project Structure

```
RegulatoryIQ-RAG/
├── ingestion/
│   ├── scrapers/
│   │   ├── base.py          # Document dataclass + BaseScraper ABC
│   │   ├── sebi.py          # SEBI circulars scraper
│   │   └── rbi.py           # RBI circulars scraper
│   └── versioning/
│       ├── hasher.py        # SHA-256 fingerprinting
│       └── store.py         # SQLite version store
├── pipeline/
│   ├── chunking/
│   │   └── structure_aware.py   # Paragraph-aware text splitter
│   ├── embedding/
│   │   └── embedder.py          # BAAI/bge-small-en-v1.5 wrapper
│   └── indexing/
│       └── qdrant_store.py      # Qdrant upsert + search
├── generation/
│   ├── generator.py         # RAG loop: retrieve → augment → generate
│   ├── guardrails.py        # Keyword-overlap grounding check
│   ├── schemas.py           # RegulatoryAnswer, Citation (Pydantic)
│   └── prompts/
│       └── templates.py     # System prompt + user prompt builder
├── backend/
│   ├── main.py              # FastAPI app + CORS
│   └── routes/
│       ├── ask.py           # POST /api/ask
│       ├── ingest.py        # POST /api/ingest
│       └── documents.py     # GET /api/documents
├── evaluation/
│   ├── dataset.py           # 10 curated SEBI/RBI Q&A pairs
│   ├── metrics.py           # Faithfulness, relevance, precision, coverage
│   ├── runner.py            # Runs eval, saves results.json
│   └── report.py            # Generates HTML scorecard
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── Sidebar.jsx      # Source filter + system status
│           ├── ChatMessage.jsx  # Answer cards with badges + citations
│           └── ChatInput.jsx    # Auto-resize textarea
├── scripts/
│   └── 10_run_eval.py       # Phase 6 evaluation entry point
├── playground/              # Step-by-step learning scripts (01–10)
├── docker-compose.yml       # Qdrant + Redis
├── requirements.txt
└── requirements-ci.txt      # Lightweight CI deps (no torch)
```

---

## Prerequisites

- Python 3.10+
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Qdrant)
- [Ollama](https://ollama.com/) (for local LLM)
- Node.js 18+ (for frontend)

---

## Setup & Run

### 1. Clone the repo

```bash
git clone https://github.com/kavin-2409/RegulatoryIQ-RAG.git
cd RegulatoryIQ-RAG
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Qdrant (vector database)

```bash
docker-compose up -d
```

Qdrant UI available at http://localhost:6333/dashboard

### 5. Start Ollama and pull the LLM

```bash
# In a separate terminal
ollama serve

# Pull phi3 (2.2 GB, one-time download)
ollama pull phi3:latest
```

### 6. Configure environment

```bash
cp .env.example .env
# No API keys needed — everything runs locally
```

### 7. Ingest documents

```bash
python playground/08_test_full_pipeline.py
```

This scrapes SEBI and RBI, chunks the documents, embeds them, and stores them in Qdrant.

### 8. Start the backend

```bash
uvicorn backend.main:app --reload
```

API running at http://localhost:8000 — docs at http://localhost:8000/docs

### 9. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — ask your first question.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System status (Qdrant, Ollama, doc count) |
| `POST` | `/api/ask` | Ask a question, get a cited answer |
| `POST` | `/api/ingest` | Trigger ingestion for SEBI or RBI |
| `GET` | `/api/documents` | List ingested documents |

**Example request:**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the CRR for commercial banks?", "regulator": "RBI", "top_k": 5}'
```

**Example response:**
```json
{
  "question": "What is the CRR for commercial banks?",
  "answer": "According to RBI directions...",
  "citations": [{"source": "RBI", "url": "https://rbi.org.in/...", "excerpt": "..."}],
  "confidence": "high",
  "grounded": true,
  "retrieved_chunks": 5
}
```

---

## Evaluation

Run the evaluation suite (requires Qdrant + Ollama running):

```bash
python scripts/10_run_eval.py
```

Opens `evaluation/report.html` — a visual scorecard with colour-coded metrics.

**Metrics (all computed locally, no OpenAI):**

| Metric | What it measures |
|---|---|
| **Faithfulness** | Are answer tokens found in the retrieved chunks? |
| **Answer relevance** | Do question keywords appear in the answer? |
| **Context precision** | Did retrieval fetch on-topic chunks? |
| **Reference coverage** | Did the answer cover expected key terms? |

---

## Known Limitations

- **SEBI detail pages are JS-rendered** — BeautifulSoup cannot execute JavaScript, so SEBI circular content falls back to the title text. Fix: use Playwright for full page rendering (planned).
- **phi3 context window** — Prompts are capped at 4096 tokens; very long circulars are truncated.
- **No authentication** — This is a local development setup. Add an auth layer before any deployment.

---

## What I Learned

This project was built as a learning journey from zero — no prior LLM/RAG/vector DB experience.

- How RAG works end-to-end: embed → retrieve → augment → generate
- Why chunking strategy matters (chunk too small = no context; too large = exceeds LLM window)
- How to evaluate a RAG system without ground-truth labels or a paid judge LLM
- The difference between a hallucinating LLM and a grounded one (guardrails)
- How to build a production-shaped Python project: typed schemas, abstract base classes, CI/CD

---

## Phases

| Phase | What was built |
|---|---|
| 1 | SEBI + RBI scrapers, document versioning with SHA-256 + SQLite |
| 2 | Structure-aware chunker, BAAI embedding model, Qdrant vector store |
| 3 | Ollama integration, RAG generator, guardrails, confidence scoring |
| 4 | FastAPI backend with typed request/response models, CORS, health check |
| 5 | React + Vite + Tailwind chat UI with source filter and citation cards |
| 6 | Evaluation framework: 4 local metrics, 10-question dataset, HTML report |

---

## License

MIT
