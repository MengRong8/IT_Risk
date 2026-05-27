from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Any

from src.dataset import load_emails
from src.detectors.hybrid import HybridDetector
from src.detectors.openrouter_llm import OpenRouterLLMDetector
from src.detectors.rule_based import RuleBasedDetector
from src.env_loader import load_dotenv_exports


def _is_correct(expected_label: str, predicted_label: str) -> bool:
    if expected_label == "phishing":
        return predicted_label == "phishing"
    return predicted_label == expected_label


def run_evaluation(
    data_dir: Path,
    output_csv: Path,
    detector_name: str = "rule_based",
) -> list[dict[str, Any]]:
    if detector_name == "rule_based":
        detector = RuleBasedDetector()
    elif detector_name in {"openrouter", "openrouter_llm"}:
        detector = OpenRouterLLMDetector()
    elif detector_name == "hybrid":
        detector = HybridDetector()
    else:
        raise ValueError(f"Unsupported detector: {detector_name}")
    emails = load_emails(data_dir)
    rows: list[dict[str, Any]] = []

    for email in emails:
        started = time.perf_counter()
        result = detector.analyze(email)
        latency_ms = round((time.perf_counter() - started) * 1000, 3)
        row = {
            "id": email["id"],
            "category": email["category"],
            "expected_label": email["expected_label"],
            "detector": result["detector"],
            "predicted_label": result["label"],
            "risk_score": result["risk_score"],
            "is_correct": _is_correct(email["expected_label"], result["label"]),
            "latency_ms": latency_ms,
            "matched_rules": ";".join(result.get("matched_rules", [])),
            "decision_source": result.get("decision_source", ""),
            "reasons": ";".join(result.get("reasons", [])),
            "suspicious_indicators": ";".join(result.get("suspicious_indicators", [])),
            "subject": email["subject"],
        }
        rows.append(row)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id", "category", "expected_label", "detector", "predicted_label",
        "risk_score", "is_correct", "latency_ms", "matched_rules", "decision_source",
        "reasons", "suspicious_indicators", "subject",
    ]
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    correct = sum(1 for row in rows if row["is_correct"] in (True, "True", "true"))
    by_category: dict[str, dict[str, Any]] = {}
    for row in rows:
        cat = row["category"]
        by_category.setdefault(cat, {"total": 0, "correct": 0})
        by_category[cat]["total"] += 1
        if row["is_correct"] in (True, "True", "true"):
            by_category[cat]["correct"] += 1
    for stats in by_category.values():
        stats["accuracy"] = round(stats["correct"] / stats["total"], 4) if stats["total"] else 0
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 4) if total else 0,
        "by_category": by_category,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AI phishing email detection experiment")
    parser.add_argument("--data-dir", type=Path, default=Path("data/emails"))
    parser.add_argument("--output-csv", type=Path, default=Path("results/email_results.csv"))
    parser.add_argument("--summary-json", type=Path, default=Path("results/summary_metrics.json"))
    parser.add_argument("--detector", default="rule_based")
    args = parser.parse_args()

    load_dotenv_exports(Path(".env"))
    rows = run_evaluation(args.data_dir, args.output_csv, args.detector)
    summary = summarize(rows)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
