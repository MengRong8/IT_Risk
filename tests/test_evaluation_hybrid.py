from pathlib import Path

import src.evaluation as evaluation


def test_run_evaluation_supports_hybrid_detector_with_injected_fake(tmp_path, monkeypatch):
    class FakeHybridDetector:
        def analyze(self, email):
            return {
                "detector": "hybrid",
                "label": email["expected_label"],
                "risk_score": 90 if email["expected_label"] == "phishing" else 5,
                "decision_source": "test_fake",
                "matched_rules": [],
                "reasons": ["fake hybrid response"],
                "suspicious_indicators": [],
            }

    monkeypatch.setattr(evaluation, "HybridDetector", FakeHybridDetector)

    rows = evaluation.run_evaluation(
        data_dir=Path("data/emails"),
        output_csv=tmp_path / "hybrid_results.csv",
        detector_name="hybrid",
    )

    assert len(rows) == 30
    assert {row["detector"] for row in rows} == {"hybrid"}
    assert all(row["is_correct"] for row in rows)
