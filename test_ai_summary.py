import io
import json
from unittest.mock import patch

import pytest

from auditor import ai_summary


@pytest.mark.parametrize("content, expected", [
    ([{"type": "text", "text": "Fix the title."}], "Fix the title."),
    ([{"type": "thinking", "thinking": "internal"},
      {"type": "text", "text": "Fix "}, {"type": "text", "text": "the title."}],
     "Fix the title."),
    ([], "(AI summary failed: response contained no text)"),
    ([{"type": "text", "text": "  "}], "(AI summary failed: response contained no text)"),
])
def test_summary_uses_all_visible_text(monkeypatch, content, expected):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    response = io.BytesIO(json.dumps({"content": content, "stop_reason": "end_turn"}).encode())
    with patch("auditor.urllib.request.urlopen", return_value=response):
        result = ai_summary("example.test", [])
    assert result.endswith(expected)
    assert "internal" not in result


@pytest.mark.parametrize("reason", ["max_tokens", "model_context_window_exceeded"])
def test_truncated_summary_is_labelled_without_retry(monkeypatch, reason):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    response = io.BytesIO(json.dumps({
        "content": [{"type": "text", "text": "Fix the"}], "stop_reason": reason,
    }).encode())
    with patch("auditor.urllib.request.urlopen", return_value=response) as request:
        result = ai_summary("example.test", [])
    assert "Fix the" in result
    assert "incomplete" in result
    request.assert_called_once()


def test_no_key_makes_no_network_request(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("auditor.urllib.request.urlopen") as request:
        assert "ANTHROPIC_API_KEY" in ai_summary("example.test", [])
    request.assert_not_called()
