from scripts.verify_live import fact_count_requires_review
from backend.app.llm import adapter


def test_live_fact_divergence_requires_review_only_above_two():
    assert not fact_count_requires_review(60, 62)
    assert not fact_count_requires_review(60, 58)
    assert fact_count_requires_review(60, 63)
    assert fact_count_requires_review(60, 57)


def test_live_extractor_sends_configured_bearer_token(monkeypatch):
    import httpx

    captured = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": '[{"text":"proposed"}]'}}]}

    def fake_post(url, headers, json, timeout):
        captured.update(url=url, headers=headers, payload=json, timeout=timeout)
        return Response()

    monkeypatch.setenv("LLM_URL", "https://model.example.test/v1/chat/completions")
    monkeypatch.setenv("LLM_API_KEY", "unit-test-token")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setattr(httpx, "post", fake_post)

    result = adapter._live_extract("source chunk", "file", 0.95, "notes.md#P1")

    assert result == [{"text": "proposed"}]
    assert captured["headers"]["Authorization"] == "Bearer unit-test-token"
    assert captured["payload"]["model"] == "test-model"
    assert captured["payload"]["temperature"] == 0
    assert captured["timeout"] == 30
