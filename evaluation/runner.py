"""
Runs the evaluation dataset through the full RAG pipeline and records results.
"""

import time
import json
from pathlib import Path
from loguru import logger

from evaluation.dataset import EVAL_DATASET
from evaluation.metrics import (
    faithfulness, answer_relevance, context_precision,
    reference_coverage, overall_score,
)
from generation.generator import RAGGenerator


def run_evaluation(output_path: str = "evaluation/results.json") -> dict:
    logger.info("Initialising RAGGenerator for evaluation ...")
    generator = RAGGenerator()

    results = []
    total = len(EVAL_DATASET)

    for i, item in enumerate(EVAL_DATASET, 1):
        qid = item["id"]
        question = item["question"]
        source_filter = item["source"]  # "SEBI" or "RBI"
        ref_terms = item["reference_terms"]

        logger.info(f"[{i}/{total}] {qid}: {question[:60]}...")
        t0 = time.perf_counter()

        try:
            # Retrieve raw chunks directly (for accurate metrics)
            query_vector = generator.embedder.embed_query(question)
            raw_chunks = generator.store.search(
                query_vector, top_k=generator.top_k, regulator=source_filter
            )

            # Generate answer
            answer_obj = generator.ask(question, regulator=source_filter)
            latency = round(time.perf_counter() - t0, 2)

            answer_text = answer_obj.answer

            faith   = faithfulness(answer_text, raw_chunks)
            rel     = answer_relevance(question, answer_text)
            prec    = context_precision(question, raw_chunks)
            ref_cov = reference_coverage(answer_text, ref_terms)
            score   = overall_score(faith, rel, prec, ref_cov)

            results.append({
                "id": qid,
                "source": source_filter,
                "question": question,
                "answer": answer_text,
                "grounded": answer_obj.grounded,
                "confidence": answer_obj.confidence,
                "retrieved_chunks": answer_obj.retrieved_chunks,
                "latency_s": latency,
                "metrics": {
                    "faithfulness": faith,
                    "answer_relevance": rel,
                    "context_precision": prec,
                    "reference_coverage": ref_cov,
                    "overall": score,
                },
                "error": None,
            })
            logger.success(f"  overall={score:.2f}  latency={latency}s")

        except Exception as exc:
            latency = round(time.perf_counter() - t0, 2)
            logger.error(f"  FAILED: {exc}")
            results.append({
                "id": qid,
                "source": source_filter,
                "question": question,
                "answer": "",
                "grounded": False,
                "confidence": "low",
                "retrieved_chunks": 0,
                "latency_s": latency,
                "metrics": {
                    "faithfulness": 0.0,
                    "answer_relevance": 0.0,
                    "context_precision": 0.0,
                    "reference_coverage": 0.0,
                    "overall": 0.0,
                },
                "error": str(exc),
            })

    # Summary statistics
    successful = [r for r in results if r["error"] is None]
    summary = {
        "total_questions": total,
        "successful": len(successful),
        "failed": total - len(successful),
        "avg_latency_s": round(
            sum(r["latency_s"] for r in successful) / len(successful), 2
        ) if successful else 0,
        "avg_metrics": {
            k: round(
                sum(r["metrics"][k] for r in successful) / len(successful), 3
            )
            for k in ["faithfulness", "answer_relevance", "context_precision",
                      "reference_coverage", "overall"]
        } if successful else {},
        "grounded_rate": round(
            sum(1 for r in successful if r["grounded"]) / len(successful), 3
        ) if successful else 0,
    }

    report = {"summary": summary, "results": results}

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {output_path}")
    return report
