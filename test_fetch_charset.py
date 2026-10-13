from email.message import Message
from io import BytesIO

import pytest

import auditor


@pytest.mark.parametrize("charset, encoding", [("iso-8859-1", "latin-1"), (None, "utf-8")])
def test_fetch_respects_http_charset_and_byte_count(monkeypatch, charset, encoding):
    raw = "<title>Café services</title>".encode(encoding)
    response = BytesIO(raw)
    response.headers = Message()
    response.headers["Content-Type"] = "text/html" + (f"; charset={charset}" if charset else "")
    monkeypatch.setattr(auditor.urllib.request, "urlopen", lambda *a, **k: response)
    html, size = auditor.fetch("https://example.com")
    assert "Café" in html
    assert size == len(raw)
    assert response.closed


def test_unknown_response_charset_has_actionable_error(monkeypatch):
    response = BytesIO(b"<title>Test</title>")
    response.headers = Message()
    response.headers["Content-Type"] = "text/html; charset=unknown-encoding"
    monkeypatch.setattr(auditor.urllib.request, "urlopen", lambda *a, **k: response)
    with pytest.raises(ValueError, match="Unsupported response charset"):
        auditor.fetch("https://example.com")
