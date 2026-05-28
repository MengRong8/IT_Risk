from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable

from flask import Flask, jsonify, request

from src.detectors.hybrid import HybridDetector
from src.detectors.openrouter_llm import OpenRouterLLMDetector
from src.detectors.rule_based import RuleBasedDetector
from src.env_loader import load_dotenv_exports

DetectorFactory = Callable[[], Any]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def create_app(
    metrics_path: Path | None = None,
    detector_factories: dict[str, DetectorFactory] | None = None,
) -> Flask:
    load_dotenv_exports(Path(".env"))

    app = Flask(__name__)
    configured_metrics_path = metrics_path or Path("results/three_detector_comparison_metrics.json")
    configured_detector_factories = detector_factories or {
        "rule_based": RuleBasedDetector,
        "openrouter": OpenRouterLLMDetector,
        "hybrid": HybridDetector,
    }

    @app.get("/health")
    def health() -> Any:
        return jsonify({
            "status": "ok",
            "detectors": list(configured_detector_factories),
            "metrics_path": str(configured_metrics_path),
        })

    @app.get("/api/email/dashboard")
    def email_dashboard() -> Any:
        metrics = _read_json(configured_metrics_path)
        hybrid_counts = metrics.get("hybrid", {}).get("decision_source_counts", {})
        cards = []
        for detector_key, label in (
            ("rule_based", "Rule-based"),
            ("openrouter_llm", "OpenRouter LLM"),
            ("hybrid", "Hybrid Detector"),
        ):
            stat = metrics[detector_key]
            cards.append({
                "key": detector_key,
                "label": label,
                "overall_pct": round(stat["overall"] * 100, 2),
                "ai_phishing_pct": round(stat["ai_phishing"] * 100, 2),
                "phishing_recall_pct": round(stat["phishing_recall"] * 100, 2),
                "false_positive_pct": round(stat["false_positive_rate"] * 100, 2),
                "avg_latency_ms": round(stat["avg_latency_ms"], 2),
                "status": "optimal" if detector_key == "hybrid" else "watch",
            })

        return jsonify({
            "story": {
                "email": "AI lowers the cost of crafting social-engineering emails, so defenders need semantic detection instead of keyword-only gateways.",
                "prompt_injection": "When enterprises deploy AI for defense or service workflows, the model itself becomes a new attack surface for prompt injection.",
            },
            "cards": cards,
            "hybrid_counts": hybrid_counts,
        })

    @app.post("/api/email/analyze")
    def email_analyze() -> Any:
        payload = request.get_json(silent=True) or {}
        subject = str(payload.get("subject", "")).strip()
        body = str(payload.get("body", "")).strip()
        detector_name = str(payload.get("detector", "hybrid")).strip().lower()

        if not subject and not body:
            return jsonify({"error": "subject or body is required"}), 400
        if detector_name not in configured_detector_factories:
            return jsonify({"error": f"Unsupported detector: {detector_name}"}), 400

        try:
            detector = configured_detector_factories[detector_name]()
            result = detector.analyze({
                "id": "dashboard-manual",
                "category": "manual",
                "subject": subject,
                "body": body,
            })
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify({
            "detector": detector_name,
            "subject": subject,
            "body": body,
            "result": result,
        })

    return app


def main() -> None:
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))


if __name__ == "__main__":
    main()