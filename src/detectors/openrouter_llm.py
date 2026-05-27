from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Callable

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

PostJson = Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]]


SYSTEM_PROMPT = """You are a defensive email security classifier for a controlled classroom lab.
Classify the email as phishing, legitimate, or uncertain.
Return ONLY valid JSON with these fields:
- label: phishing|legitimate|uncertain
- risk_score: integer 0-100
- reasons: array of short strings
- suspicious_indicators: array of short strings
Do not include markdown or extra prose.
"""


def default_post_json(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=60) as response:  # nosec - fixed trusted API endpoint
        return json.loads(response.read().decode("utf-8"))


class OpenRouterLLMDetector:
    """OpenRouter-backed defensive phishing classifier."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float = 0,
        max_tokens: int = 800,
        post_json: PostJson = default_post_json,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.model = model or os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.post_json = post_json
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required for OpenRouterLLMDetector")

    def analyze(self, email: dict[str, Any]) -> dict[str, Any]:
        subject = email.get("subject", "")
        body = email.get("body", "")
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Subject: {subject}\n\nBody:\n{body}",
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://example.com/genai-security-lab",
            "X-Title": "GenAI Security Lab Email Detection",
        }
        response = self.post_json(OPENROUTER_URL, headers, payload)
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

        try:
            parsed = json.loads(content)
            label = parsed.get("label", "uncertain")
            if label not in {"phishing", "legitimate", "uncertain"}:
                label = "uncertain"
            risk_score = int(parsed.get("risk_score", 50))
            risk_score = max(0, min(100, risk_score))
            return {
                "detector": "openrouter_llm",
                "label": label,
                "risk_score": risk_score,
                "reasons": parsed.get("reasons", []),
                "suspicious_indicators": parsed.get("suspicious_indicators", []),
                "raw_content": content,
                "usage": response.get("usage", {}),
            }
        except Exception as exc:  # deliberately defensive: raw output is preserved
            return {
                "detector": "openrouter_llm",
                "label": "uncertain",
                "risk_score": 50,
                "reasons": [],
                "suspicious_indicators": [],
                "raw_content": content,
                "usage": response.get("usage", {}),
                "parse_error": str(exc),
            }
