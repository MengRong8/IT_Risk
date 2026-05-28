import json

from src.detector_api import create_app


class FakeDetector:
    def __init__(self, label="phishing", score=77):
        self.label = label
        self.score = score

    def analyze(self, email):
        return {
            "detector": "fake",
            "label": self.label,
            "risk_score": self.score,
            "matched_rules": ["fake_rule"],
        }


def test_detector_api_returns_dashboard_payload(tmp_path):
    metrics_path = tmp_path / "metrics.json"
    metrics_path.write_text(json.dumps({
        "rule_based": {"overall": 0.7, "ai_phishing": 0.3, "phishing_recall": 0.5, "false_positive_rate": 0.0, "avg_latency_ms": 1.2},
        "openrouter_llm": {"overall": 0.8, "ai_phishing": 0.6, "phishing_recall": 0.7, "false_positive_rate": 0.0, "avg_latency_ms": 4500},
        "hybrid": {"overall": 0.9, "ai_phishing": 0.7, "phishing_recall": 0.85, "false_positive_rate": 0.0, "avg_latency_ms": 669, "decision_source_counts": {"llm_escalation": 6, "rule_based_confident": 24}},
    }), encoding="utf-8")
    app = create_app(metrics_path=metrics_path)

    response = app.test_client().get("/api/email/dashboard")
    body = response.get_json()

    assert response.status_code == 200
    assert len(body["cards"]) == 3
    assert body["cards"][2]["label"] == "Hybrid Detector"
    assert body["hybrid_counts"]["llm_escalation"] == 6


def test_detector_api_analyzes_manual_email_with_injected_detector():
    app = create_app(detector_factories={"rule_based": lambda: FakeDetector()})

    response = app.test_client().post(
        "/api/email/analyze",
        json={
            "detector": "rule_based",
            "subject": "verify your account",
            "body": "please sign in now",
        },
    )
    body = response.get_json()

    assert response.status_code == 200
    assert body["result"]["label"] == "phishing"
    assert body["result"]["risk_score"] == 77