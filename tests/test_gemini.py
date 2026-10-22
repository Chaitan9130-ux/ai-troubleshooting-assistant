import copy
import json
from pathlib import Path
import sys
from urllib.error import HTTPError
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gemini
from retrieval import Retriever


@pytest.fixture
def matched():
    return Retriever().search("Payment API 500")


def valid_payload(result):
    entry = result.matches[0].entry
    return {"supported": True, "source_id": entry["id"],
            "assessment": "This may match the payment API error runbook; confirm the symptoms.",
            "diagnostic_checks": entry["diagnostic_checks"], "resolution": entry["resolution"],
            "escalation_team": entry["escalation_team"]}


def envelope(payload, finish="STOP"):
    return {"candidates": [{"finishReason": finish, "content": {"parts": [{"text": json.dumps(payload)}]}}]}


def test_valid_generation_request_and_result(matched):
    transport = Mock(return_value=envelope(valid_payload(matched)))
    answer = gemini.generate_answer("Payment API 500", matched, "dummy-test-key", transport=transport)
    assert answer.mode == "gemini"
    url, payload, key = transport.call_args.args
    assert url.startswith("https://generativelanguage.googleapis.com/")
    assert "dummy-test-key" not in url
    assert payload["generationConfig"]["responseMimeType"] == "application/json"
    data = json.loads(payload["contents"][0]["parts"][0]["text"])
    assert data["runbook"]["id"] == "KB-001"
    assert "untrusted DATA" in payload["systemInstruction"]["parts"][0]["text"]


@pytest.mark.parametrize("query", ["", "My keyboard is broken", "The service is down"])
def test_no_call_without_retrieval_evidence(query):
    transport = Mock()
    result = gemini.generate_answer(query, Retriever().search(query), "dummy", transport=transport)
    assert result.mode == "offline"
    transport.assert_not_called()


def test_missing_key_and_invalid_model_do_not_call(matched):
    transport = Mock()
    assert gemini.generate_answer("q", matched, transport=transport).mode == "offline"
    assert gemini.generate_answer("q", matched, "dummy", "../../evil", transport).mode == "offline"
    transport.assert_not_called()


@pytest.mark.parametrize("field,value", [
    ("source_id", "KB-INVENTED"),
    ("resolution", "Delete the database immediately."),
    ("diagnostic_checks", ["Restart production without checking logs."]),
    ("escalation_team", "Invented team"),
    ("supported", False),
    ("assessment", ""),
    ("assessment", "a" * 1201),
])
def test_unsupported_guidance_is_discarded(matched, field, value):
    data = copy.deepcopy(valid_payload(matched))
    data[field] = value
    result = gemini.generate_answer("q", matched, "dummy", transport=lambda *args: envelope(data))
    assert result.mode == "offline"
    assert result.assessment == ""


@pytest.mark.parametrize("response", [
    {}, {"candidates": []}, envelope({}, "MAX_TOKENS"),
    {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "not json"}]}}]},
])
def test_malformed_blocked_and_truncated_outputs_fall_back(matched, response):
    result = gemini.generate_answer("q", matched, "dummy", transport=lambda *args: response)
    assert result.mode == "offline"


def test_timeout_and_raw_errors_are_never_exposed(matched):
    for error in [TimeoutError("secret-in-error"), RuntimeError("secret-in-error")]:
        result = gemini.generate_answer("q", matched, "dummy", transport=Mock(side_effect=error))
        assert result.mode == "offline"
        assert "secret-in-error" not in result.notice


def test_http_error_sanitized(monkeypatch):
    error = HTTPError("https://example.invalid/?secret", 429, "secret-in-error", {}, None)
    monkeypatch.setattr(gemini, "build_opener", lambda *args: Mock(open=Mock(side_effect=error)))
    with pytest.raises(gemini.GeminiError, match="quota or rate limit") as exc:
        gemini.post_json("https://example.invalid", {}, "dummy")
    assert "secret" not in str(exc.value)


def test_transport_headers_timeout_and_response_limit(monkeypatch):
    response = Mock()
    response.read.return_value = b'{"candidates": []}'
    context = Mock()
    context.__enter__ = Mock(return_value=response)
    context.__exit__ = Mock(return_value=False)
    opener = Mock(open=Mock(return_value=context))
    monkeypatch.setattr(gemini, "build_opener", lambda *args: opener)
    gemini.post_json("https://generativelanguage.googleapis.com/test", {"x": 1}, "dummy")
    request = opener.open.call_args.args[0]
    assert request.get_header("X-goog-api-key") == "dummy"
    assert opener.open.call_args.kwargs["timeout"] == 20
    response.read.assert_called_once_with(gemini.MAX_RESPONSE_BYTES + 1)


def test_redirects_not_followed():
    assert gemini.NoRedirects().redirect_request(None, None, 302, "", {}, "https://evil.invalid") is None
