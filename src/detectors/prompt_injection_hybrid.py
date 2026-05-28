from __future__ import annotations

import re
from typing import Any

from src.detectors.prompt_injection_openrouter import PromptInjectionOpenRouterDetector
from src.detectors.prompt_injection_rule_based import PromptInjectionRuleBasedDetector


class PromptInjectionHybridDetector:
    """Layered prompt guard: rules first, LLM escalation for uncertain prompts."""

    meta_targets = (
        "hidden",
        "internal",
        "system",
        "prompt",
        "instruction",
        "behavior",
        "policy",
        "guardrail",
        "token",
        "secret",
    )
    action_verbs = (
        "restate",
        "repeat",
        "reveal",
        "show",
        "print",
        "dump",
        "describe",
        "ignore",
        "bypass",
        "override",
    )
    laundering_verbs = (
        "translate",
        "reproduce",
        "repeat exactly",
        "echo",
        "spell",
        "normalize",
        "compare the spelling",
    )
    protected_markers = (
        "protected phrase",
        "protected string",
        "confidential_flag",
        "lab_secret",
        "secret",
        "token",
        "flag",
    )

    def __init__(
        self,
        rule_detector: Any | None = None,
        llm_detector: Any | None = None,
    ) -> None:
        self.rule_detector = rule_detector or PromptInjectionRuleBasedDetector()
        self.llm_detector = llm_detector or PromptInjectionOpenRouterDetector()

    def _should_escalate_allow(self, prompt: dict[str, Any], rule_result: dict[str, Any]) -> bool:
        if rule_result["label"] != "allow":
            return False

        text = str(prompt.get("message", "")).lower()
        if rule_result.get("matched_rules"):
            return True

        has_meta_target = any(re.search(rf"\b{re.escape(term)}\b", text) for term in self.meta_targets)
        has_action_verb = any(re.search(rf"\b{re.escape(term)}\b", text) for term in self.action_verbs)
        if has_meta_target and has_action_verb:
            return True

        has_laundering_verb = any(term in text for term in self.laundering_verbs)
        has_protected_marker = any(term in text for term in self.protected_markers)
        return has_laundering_verb and has_protected_marker

    def analyze(self, prompt: dict[str, Any]) -> dict[str, Any]:
        rule_result = self.rule_detector.analyze(prompt)

        if rule_result["label"] == "block":
            return {
                "detector": "prompt_hybrid",
                "label": rule_result["label"],
                "risk_score": rule_result["risk_score"],
                "decision_source": "rule_based_confident",
                "matched_rules": rule_result.get("matched_rules", []),
                "reasons": [],
                "rule_result": rule_result,
                "llm_result": None,
            }

        if rule_result["label"] == "allow" and not self._should_escalate_allow(prompt, rule_result):
            return {
                "detector": "prompt_hybrid",
                "label": rule_result["label"],
                "risk_score": rule_result["risk_score"],
                "decision_source": "rule_based_confident",
                "matched_rules": rule_result.get("matched_rules", []),
                "reasons": [],
                "rule_result": rule_result,
                "llm_result": None,
            }

        llm_result = self.llm_detector.analyze(prompt)
        return {
            "detector": "prompt_hybrid",
            "label": llm_result["label"],
            "risk_score": llm_result["risk_score"],
            "decision_source": "llm_escalation",
            "matched_rules": rule_result.get("matched_rules", []),
            "reasons": llm_result.get("reasons", []),
            "rule_result": rule_result,
            "llm_result": llm_result,
        }