from pathlib import Path

from src.evaluation import run_evaluation
from src.plots import create_detection_rate_chart


def test_create_detection_rate_chart_writes_png(tmp_path):
    output_csv = tmp_path / "email_results.csv"
    chart_path = tmp_path / "detection_rate_by_category.png"
    rows = run_evaluation(
        data_dir=Path("data/emails"),
        output_csv=output_csv,
        detector_name="rule_based",
    )

    create_detection_rate_chart(rows, chart_path)

    assert chart_path.exists()
    assert chart_path.stat().st_size > 0
