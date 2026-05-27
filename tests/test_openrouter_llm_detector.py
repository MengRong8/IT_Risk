from src.detectors.openrouter_llm import OpenRouterLLMDetector


def test_openrouter_detector_parses_json_content_from_fake_response():
    calls = []

    def fake_post_json(url, headers, payload):
        calls.append((url, headers, payload))
        return {
            "choices": [
                {
                    "message": {
                        "content": '{"label":"phishing","risk_score":87,"reasons":["requests account verification"],"suspicious_indicators":["credential request"]}'
                    }
                }
            ],
            "usage": {"total_tokens": 123},
        }

    detector = OpenRouterLLMDetector(
        api_key="test-key",
        model="test/model",
        post_json=fake_post_json,
    )

    result = detector.analyze({
        "subject": "Please verify your account",
        "body": "Use the temporary login page to verify access.",
    })

    assert result["detector"] == "openrouter_llm"
    assert result["label"] == "phishing"
    assert result["risk_score"] == 87
    assert result["usage"]["total_tokens"] == 123
    assert calls[0][1]["Authorization"] == "Bearer test-key"
    assert calls[0][2]["model"] == "test/model"


def test_openrouter_detector_returns_uncertain_on_invalid_json():
    def fake_post_json(url, headers, payload):
        return {"choices": [{"message": {"content": "not json"}}]}

    detector = OpenRouterLLMDetector(
        api_key="test-key",
        model="test/model",
        post_json=fake_post_json,
    )

    result = detector.analyze({"subject": "Hello", "body": "Normal update"})

    assert result["label"] == "uncertain"
    assert result["risk_score"] == 50
    assert "parse_error" in result
