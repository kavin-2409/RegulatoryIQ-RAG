"""
Phase 3 end-to-end test — full RAG pipeline.

Requires:
  - Qdrant running:  docker-compose up -d
  - Ollama running:  ollama serve  (or it starts automatically)
  - Documents in Qdrant: run playground/08_test_full_pipeline.py first
"""
import sys
sys.path.insert(0, ".")

from generation.generator import RAGGenerator

print("=" * 60)
print("PHASE 3: RegulatorIQ — Question Answering Demo")
print("Model: phi3:latest (running locally via Ollama)")
print("=" * 60)
print()

generator = RAGGenerator(top_k=3)

questions = [
    {
        "q": "What are the SEBI rules on cybersecurity incident reporting?",
        "filter": "SEBI",
    },
    {
        "q": "What is the cash reserve ratio for commercial banks as per RBI?",
        "filter": "RBI",
    },
    {
        "q": "What are the price band rules for ETFs in the pre-open session?",
        "filter": None,
    },
]

for item in questions:
    print(f"QUESTION: {item['q']}")
    if item["filter"]:
        print(f"Filter:   {item['filter']} only")
    print("-" * 60)

    result = generator.ask(item["q"], regulator=item["filter"])

    print(f"ANSWER:\n{result.answer}")
    print()
    print(f"Confidence:  {result.confidence}")
    print(f"Grounded:    {result.grounded}")
    print(f"Chunks used: {result.retrieved_chunks}")
    print()

    if result.citations:
        print("CITATIONS:")
        for c in result.citations:
            print(f"  Source: {c.source}")
            print(f"  Doc ID: {c.doc_id}")
            if c.url:
                print(f"  URL:    {c.url}")
            print(f"  Text:   {c.excerpt[:120]}...")
            print()

    print("=" * 60)
    print()
