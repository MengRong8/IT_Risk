from pathlib import Path

import src.evaluation as evaluation


def test_run_evaluation_supports_openrouter_detector_with_injected_fake(tmp_path, monkeypatch):
    class FakeOpenRouterDetector:
        def __init__(self):
            pass

        def analyze(self, email):
            return {
                "detector": "openrouter_llm",
                "label": email["expected_label"],
                "risk_score": 80 if email["expected_label"] == "phishing" else 10,
                "reasons": ["fake test response"],
                "suspicious_indicators": [],
            }

    monkeypatch.setattr(evaluation, "OpenRouterLLMDetector", FakeOpenRouterDetector)

    rows = evaluation.run_evaluation(
        data_dir=Path("data/emails"),
        output_csv=tmp_path / "openrouter_results.csv",
        detector_name="openrouter",
    )

    assert len(rows) == 30
    assert {row["detector"] for row in rows} == {"openrouter_llm"}
    assert all(row["is_correct"] for row in rows)
