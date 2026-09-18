from contextlib import nullcontext
from types import SimpleNamespace
from urllib.error import HTTPError

import pytest

import auditor


def test_only_http_links_are_checked_with_scheme_and_whitespace_normalized(monkeypatch):
    requests = []

    def open_link(request, **kwargs):
        requests.append(request.full_url)
        return nullcontext(SimpleNamespace(status=200))

    monkeypatch.setattr(auditor.urllib.request, "urlopen", open_link)
    rows = auditor.check_links([" MAILTO:hello@example.com ", "tel:123", "data:text/plain,hi",
                                "ftp://example.com/file", " /help "], "https://example.com")
    assert requests == ["https://example.com/help"]
    assert rows == [(auditor.PASS, "Link check", "Checked 1 links — none broken.")]


def test_fragments_do_not_consume_duplicate_request_slots(monkeypatch):
    urls = []

    def open_link(request, **kwargs):
        urls.append(request.full_url)
        return nullcontext(SimpleNamespace(status=200))

    monkeypatch.setattr(auditor.urllib.request, "urlopen", open_link)
    auditor.check_links(["/docs#one", "/docs#two", "/contact"], "https://example.com", cap=2)
    assert urls == ["https://example.com/docs", "https://example.com/contact"]


@pytest.mark.parametrize("code", [405, 501])
def test_head_not_supported_falls_back_to_get(monkeypatch, code):
    methods = []

    def open_link(request, **kwargs):
        methods.append(request.get_method())
        if request.get_method() == "HEAD":
            raise HTTPError(request.full_url, code, "Unsupported method", {}, None)
        return nullcontext(SimpleNamespace(status=200))

    monkeypatch.setattr(auditor.urllib.request, "urlopen", open_link)
    rows = auditor.check_links(["/valid"], "https://example.com")
    assert methods == ["HEAD", "GET"]
    assert rows[0][0] == auditor.PASS


def test_fallback_preserves_broken_get_result(monkeypatch):
    def open_link(request, **kwargs):
        code = 405 if request.get_method() == "HEAD" else 404
        raise HTTPError(request.full_url, code, "error", {}, None)

    monkeypatch.setattr(auditor.urllib.request, "urlopen", open_link)
    assert auditor.check_links(["/missing"], "https://example.com")[0][0] == auditor.FAIL


def test_report_write_error_has_clear_message_and_exit_code(tmp_path, capsys):
    source = tmp_path / "page.html"
    source.write_text("<h1>Example</h1>", encoding="utf-8")
    assert auditor.main(["--file", str(source), "--out", str(tmp_path)]) == 2
    assert "Could not write report" in capsys.readouterr().err
