"""
Phase 6 — Evaluation entry point.

Usage (from project root, with venv active):
    python scripts/10_run_eval.py

Requirements:
    - Qdrant running  (docker-compose up -d)
    - Ollama running  (ollama serve)
    - phi3 pulled     (ollama pull phi3:latest)
    - Documents already ingested (run 08_test_full_pipeline.py first if needed)
"""

import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger
from evaluation.runner import run_evaluation
from evaluation.report import generate_report

RESULTS_PATH = "evaluation/results.json"
REPORT_PATH  = "evaluation/report.html"

if __name__ == "__main__":
    logger.info("=== RegulatorIQ Evaluation — Phase 6 ===")

    report_data = run_evaluation(output_path=RESULTS_PATH)
    summary = report_data["summary"]

    logger.info("Generating HTML report ...")
    generate_report(results_path=RESULTS_PATH, output_path=REPORT_PATH)

    logger.info("")
    logger.info("=== SUMMARY ===")
    logger.info(f"Questions : {summary['total_questions']}  "
                f"(passed: {summary['successful']}, failed: {summary['failed']})")
    logger.info(f"Avg latency  : {summary['avg_latency_s']}s")
    logger.info(f"Grounded rate: {int(summary['grounded_rate'] * 100)}%")
    if summary["avg_metrics"]:
        m = summary["avg_metrics"]
        logger.info(f"Faithfulness : {m['faithfulness']:.2f}")
        logger.info(f"Ans relevance: {m['answer_relevance']:.2f}")
        logger.info(f"Ctx precision: {m['context_precision']:.2f}")
        logger.info(f"Ref coverage : {m['reference_coverage']:.2f}")
        logger.info(f"OVERALL SCORE: {m['overall']:.2f}")
    logger.info(f"HTML report  : {REPORT_PATH}")
