from src.dashboard_frontend import create_app


def test_dashboard_frontend_proxies_email_dashboard(monkeypatch):
    def fake_request_json(url, method="GET", payload=None):
        assert url.endswith("/api/email/dashboard")
        return 200, {"cards": [{"label": "Hybrid Detector"}]}

    monkeypatch.setattr("src.dashboard_frontend._request_json", fake_request_json)
    app = create_app(detector_api_base="http://detector-api", chatbot_api_base="http://chatbot")

    response = app.test_client().get("/api/dashboard/email")

    assert response.status_code == 200
    assert response.get_json()["cards"][0]["label"] == "Hybrid Detector"


def test_dashboard_frontend_proxies_chatbot(monkeypatch):
    def fake_request_json(url, method="GET", payload=None):
        assert url.endswith("/api/chat")
        assert method == "POST"
        assert payload["guard_mode"] == "llm"
        return 403, {"status": "blocked", "response": None}

    monkeypatch.setattr("src.dashboard_frontend._request_json", fake_request_json)
    app = create_app(detector_api_base="http://detector-api", chatbot_api_base="http://chatbot")

    response = app.test_client().post(
        "/api/dashboard/chat",
        json={"guard_mode": "llm", "message": "attack"},
    )

    assert response.status_code == 403
    assert response.get_json()["status"] == "blocked"


def test_dashboard_frontend_proxies_chatbot_batch_evaluate(monkeypatch):
    def fake_request_json(url, method="GET", payload=None):
        assert url.endswith("/api/batch-evaluate")
        assert method == "POST"
        assert payload["guard_mode"] == "hybrid"
        assert payload["payload_dir"] == "data/promt_injection"
        return 200, {"total": 6, "blocked": 5, "allowed": 1, "results": []}

    monkeypatch.setattr("src.dashboard_frontend._request_json", fake_request_json)
    app = create_app(detector_api_base="http://detector-api", chatbot_api_base="http://chatbot")

    response = app.test_client().post(
        "/api/dashboard/chat/batch-evaluate",
        json={"guard_mode": "hybrid", "payload_dir": "data/promt_injection"},
    )

    assert response.status_code == 200
    assert response.get_json()["blocked"] == 5