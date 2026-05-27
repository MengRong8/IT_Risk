from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = {"id", "category", "expected_label", "subject", "body"}
EXPECTED_CATEGORIES = ("normal", "traditional_phishing", "ai_phishing")


def load_emails(data_dir: Path) -> list[dict[str, Any]]:
    """Load email JSON samples recursively from data_dir."""
    emails: list[dict[str, Any]] = []
    for path in sorted(data_dir.rglob("*.json")):
        with path.open(encoding="utf-8") as f:
            email = json.load(f)
        email["_path"] = str(path)
        emails.append(email)
    return emails


def validate_dataset(emails: list[dict[str, Any]]) -> dict[str, Any]:
    missing_required_fields: list[dict[str, Any]] = []
    for email in emails:
        missing = sorted(REQUIRED_FIELDS - set(email))
        if missing:
            missing_required_fields.append({
                "id": email.get("id", "<missing id>"),
                "missing": missing,
            })

    return {
        "total": len(emails),
        "by_category": dict(Counter(email.get("category") for email in emails)),
        "missing_required_fields": missing_required_fields,
    }
