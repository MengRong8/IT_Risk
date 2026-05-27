from src.detectors.rule_based import RuleBasedDetector


def test_rule_based_detector_flags_credential_request_with_urgency():
    detector = RuleBasedDetector()
    email = {
        "subject": "Final notice: verify your account today",
        "body": "Please login immediately to verify your password within 24 hours: http://example.com/login",
    }

    result = detector.analyze(email)

    assert result["label"] == "phishing"
    assert result["risk_score"] >= 60
    assert "credential_request" in result["matched_rules"]
    assert "urgency" in result["matched_rules"]


def test_rule_based_detector_keeps_normal_meeting_notice_legitimate():
    detector = RuleBasedDetector()
    email = {
        "subject": "Project meeting reminder",
        "body": "Hi team, our weekly project meeting is tomorrow at 10 AM. Please bring your status updates.",
    }

    result = detector.analyze(email)

    assert result["label"] == "legitimate"
    assert result["risk_score"] < 30
