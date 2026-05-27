from __future__ import annotations

from typing import Any

from src.detectors.openrouter_llm import OpenRouterLLMDetector
from src.detectors.rule_based import RuleBasedDetector


class HybridDetector:
    """Layered detector: use cheap rules first, escalate uncertain cases to LLM."""

    def __init__(
        self,
        rule_detector: Any | None = None,
        llm_detector: Any | None = None,
    ) -> None:
        self.rule_detector = rule_detector or RuleBasedDetector()
        self.llm_detector = llm_detector or OpenRouterLLMDetector()

    def analyze(self, email: dict[str, Any]) -> dict[str, Any]:
        rule_result = self.rule_detector.analyze(email)

        if rule_result["label"] in {"phishing", "legitimate"}:
            return {
                "detector": "hybrid",
                "label": rule_result["label"],
                "risk_score": rule_result["risk_score"],
                "decision_source": "rule_based_confident",
                "matched_rules": rule_result.get("matched_rules", []),
                "reasons": [],
                "suspicious_indicators": [],
                "rule_result": rule_result,
                "llm_result": None,
            }

        llm_result = self.llm_detector.analyze(email)
        return {
            "detector": "hybrid",
            "label": llm_result["label"],
            "risk_score": llm_result["risk_score"],
            "decision_source": "llm_escalation",
            "matched_rules": rule_result.get("matched_rules", []),
            "reasons": llm_result.get("reasons", []),
            "suspicious_indicators": llm_result.get("suspicious_indicators", []),
            "rule_result": rule_result,
            "llm_result": llm_result,
        }
