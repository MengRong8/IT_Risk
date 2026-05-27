import csv
from pathlib import Path

from src.evaluation import run_evaluation


def test_run_evaluation_writes_csv_with_one_rule_result_per_email(tmp_path):
    output_csv = tmp_path / "email_results.csv"

    rows = run_evaluation(
        data_dir=Path("data/emails"),
        output_csv=output_csv,
        detector_name="rule_based",
    )

    assert len(rows) == 30
    assert output_csv.exists()

    with output_csv.open(newline="", encoding="utf-8") as f:
        loaded = list(csv.DictReader(f))

    assert len(loaded) == 30
    assert set(loaded[0]) >= {
        "id",
        "category",
        "expected_label",
        "detector",
        "predicted_label",
        "risk_score",
        "is_correct",
        "matched_rules",
    }
