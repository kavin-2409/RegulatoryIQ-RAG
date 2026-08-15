# RegulatorIQ

**Multi-source regulatory change intelligence for compliance teams.**

RegulatorIQ ingests regulatory documents from SEC EDGAR and the Federal Register, tracks version changes over time, and lets users ask cross-document questions like _"How does this new SEC rule affect our current data retention policy?"_ — returning structured answers with citations and gap analysis.

---

## Architecture

> Architecture diagram coming soon.

## Tech Stack

| Layer | Technology |
|---|---|
| Vector DB | Qdrant |
| Embeddings | text-embedding-3-large / bge-large-en-v1.5 |
| LLM | Claude / GPT-4o |
| Backend | FastAPI + Celery + Redis |
| Frontend | Next.js 14 + shadcn/ui |
| Scheduling | Prefect |
| Evaluation | Ragas |

## Local Development

```bash
# 1. Start Qdrant + Redis
docker-compose up -d

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# edit .env and add your API keys

# 5. Run the backend
uvicorn backend.main:app --reload
```

## Evaluation

> Eval scores and charts coming once the golden dataset is built.
