from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PromptRule:
    name: str
    weight: int
    patterns: tuple[str, ...]


class PromptInjectionRuleBasedDetector:
    """Cheap lexical prompt-injection detector for lab comparisons."""

    def __init__(self) -> None:
        self.rules = (
            PromptRule(
                "instruction_override",
                40,
                (
                    r"ignore previous instructions",
                    r"ignore all previous",
                    r"disregard the above",
                    r"forget the earlier instructions",
                ),
            ),
            PromptRule(
                "system_prompt_probe",
                35,
                (
                    r"system prompt",
                    r"developer message",
                    r"hidden prompt",
                    r"internal instructions",
                    r"hidden guidance",
                    r"behavioral instructions",
                    r"what rules govern you",
                ),
            ),
            PromptRule(
                "policy_bypass",
                30,
                (
                    r"bypass safety",
                    r"disable filters",
                    r"jailbreak",
                    r"without restrictions",
                    r"ignore your safety",
                    r"override your policy",
                ),
            ),
            PromptRule(
                "secret_exfiltration",
                30,
                (
                    r"reveal the secret",
                    r"show me the api key",
                    r"print the password",
                    r"dump the token",
                    r"internal token",
                    r"restate the hidden",
                    r"reveal your instructions",
                    r"show your hidden guidance",
                    r"how you were instructed",
                ),
            ),
            PromptRule(
                "meta_behavior_probe",
                20,
                (
                    r"defines your behavior",
                    r"what defines your behavior",
                    r"how you were configured",
                    r"how you are governed",
                    r"how you should behave",
                ),
            ),
        )

    def analyze(self, prompt: dict[str, Any]) -> dict[str, Any]:
        text = str(prompt.get("message", "")).lower()
        matched_rules: list[str] = []
        score = 0

        for rule in self.rules:
            if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in rule.patterns):
                matched_rules.append(rule.name)
                score += rule.weight

        score = min(score, 100)
        if score >= 60:
            label = "block"
        elif score >= 25:
            label = "uncertain"
        else:
            label = "allow"

        return {
            "detector": "prompt_rule_based",
            "label": label,
            "risk_score": score,
            "matched_rules": matched_rules,
        }