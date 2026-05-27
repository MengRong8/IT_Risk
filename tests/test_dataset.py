from pathlib import Path

from src.dataset import load_emails, validate_dataset


def test_load_emails_reads_all_30_json_samples():
    emails = load_emails(Path("data/emails"))

    assert len(emails) == 30
    assert {email["category"] for email in emails} == {
        "normal",
        "traditional_phishing",
        "ai_phishing",
    }


def test_validate_dataset_requires_balanced_categories_and_fields():
    emails = load_emails(Path("data/emails"))
    summary = validate_dataset(emails)

    assert summary["total"] == 30
    assert summary["by_category"] == {
        "normal": 10,
        "traditional_phishing": 10,
        "ai_phishing": 10,
    }
    assert summary["missing_required_fields"] == []
