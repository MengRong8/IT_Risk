from src.detectors.hybrid import HybridDetector


class FakeRuleDetector:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def analyze(self, email):
        self.calls += 1
        return self.result


class FakeLLMDetector:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def analyze(self, email):
        self.calls += 1
        return self.result


def test_hybrid_accepts_confident_rule_based_phishing_without_llm_call():
    rule = FakeRuleDetector({
        "detector": "rule_based",
        "label": "phishing",
        "risk_score": 85,
        "matched_rules": ["urgency", "credential_request"],
    })
    llm = FakeLLMDetector({"detector": "openrouter_llm", "label": "legitimate", "risk_score": 10})

    result = HybridDetector(rule_detector=rule, llm_detector=llm).analyze({"subject": "x", "body": "y"})

    assert result["label"] == "phishing"
    assert result["risk_score"] == 85
    assert result["decision_source"] == "rule_based_confident"
    assert llm.calls == 0


def test_hybrid_escalates_uncertain_rule_result_to_llm():
    rule = FakeRuleDetector({
        "detector": "rule_based",
        "label": "uncertain",
        "risk_score": 40,
        "matched_rules": ["financial_action"],
    })
    llm = FakeLLMDetector({
        "detector": "openrouter_llm",
        "label": "phishing",
        "risk_score": 85,
        "reasons": ["semantic social engineering"],
        "suspicious_indicators": ["payment details request"],
    })

    result = HybridDetector(rule_detector=rule, llm_detector=llm).analyze({"subject": "x", "body": "y"})

    assert result["label"] == "phishing"
    assert result["risk_score"] == 85
    assert result["decision_source"] == "llm_escalation"
    assert llm.calls == 1
    assert result["rule_result"]["risk_score"] == 40
    assert result["llm_result"]["risk_score"] == 85


def test_hybrid_accepts_confident_rule_based_legitimate_without_llm_call():
    rule = FakeRuleDetector({
        "detector": "rule_based",
        "label": "legitimate",
        "risk_score": 0,
        "matched_rules": [],
    })
    llm = FakeLLMDetector({"detector": "openrouter_llm", "label": "phishing", "risk_score": 85})

    result = HybridDetector(rule_detector=rule, llm_detector=llm).analyze({"subject": "x", "body": "y"})

    assert result["label"] == "legitimate"
    assert result["decision_source"] == "rule_based_confident"
    assert llm.calls == 0
