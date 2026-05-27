from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Rule:
    name: str
    weight: int
    patterns: tuple[str, ...]


class RuleBasedDetector:
    """Simple explainable phishing detector for a controlled classroom lab."""

    def __init__(self) -> None:
        self.rules = (
            Rule("credential_request", 35, (
                r"\bpassword\b", r"\blogin\b", r"verify your account", r"account verification",
                r"更新密碼", r"驗證帳號", r"登入", r"帳號驗證",
            )),
            Rule("urgency", 25, (
                r"urgent", r"immediately", r"within 24 hours", r"final notice",
                r"立即", r"今天內", r"24 小時", r"最後通知", r"盡快",
            )),
            Rule("financial_action", 25, (
                r"wire transfer", r"payment", r"invoice", r"bank account",
                r"匯款", r"付款", r"發票", r"銀行帳戶", r"退款", r"報銷",
            )),
            Rule("suspicious_url", 30, (
                r"http://", r"bit\.ly", r"tinyurl", r"login[-.]", r"verify[-.]",
                r"example\.com/login", r"demo\.invalid",
            )),
            Rule("attachment_lure", 15, (
                r"attachment", r"attached", r"statement", r"receipt",
                r"附件", r"報表", r"收據", r"對帳單",
            )),
            Rule("impersonation", 20, (
                r"it department", r"human resources", r"finance team", r"system administrator",
                r"資訊部", r"人資", r"財務部", r"校務系統", r"主管",
            )),
            Rule("external_pressure", 15, (
                r"avoid suspension", r"account will be closed", r"access will expire",
                r"停權", r"帳號將關閉", r"權限到期",
            )),
        )

    def analyze(self, email: dict[str, Any]) -> dict[str, Any]:
        text = f"{email.get('subject', '')}\n{email.get('body', '')}".lower()
        matched_rules: list[str] = []
        score = 0

        for rule in self.rules:
            if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in rule.patterns):
                matched_rules.append(rule.name)
                score += rule.weight

        score = min(score, 100)
        if score >= 60:
            label = "phishing"
        elif score >= 30:
            label = "uncertain"
        else:
            label = "legitimate"

        return {
            "detector": "rule_based",
            "label": label,
            "risk_score": score,
            "matched_rules": matched_rules,
        }
