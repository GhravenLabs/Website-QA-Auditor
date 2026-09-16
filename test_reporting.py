from contextlib import nullcontext
from types import SimpleNamespace

import auditor
import pytest


def test_ai_summary_is_generated_once_for_console_and_report(tmp_path, monkeypatch, capsys):
    source = tmp_path / "page.html"
    source.write_text("<title>Example</title>", encoding="utf-8")
    report = tmp_path / "report.md"
    calls = []

    def summary(*args):
        calls.append(args)
        return "Unique generated summary"

    monkeypatch.setattr(auditor, "ai_summary", summary)
    auditor.main(["--file", str(source), "--ai", "--out", str(report)])
    assert len(calls) == 1
    assert "Unique generated summary" in capsys.readouterr().out
    assert "Unique generated summary" in report.read_text(encoding="utf-8")


@pytest.mark.parametrize("cap", [0, 1, 2])
def test_link_count_matches_requests_at_cap(monkeypatch, cap):
    requested = []

    def open_link(request, **kwargs):
        requested.append(request.full_url)
        return nullcontext(SimpleNamespace(status=200))

    monkeypatch.setattr(auditor.urllib.request, "urlopen", open_link)
    rows = auditor.check_links(["/a", "/a", "/b", "/c"], "https://example.com", cap)
    assert len(requested) == cap
    assert rows == [(auditor.PASS, "Link check", f"Checked {cap} links — none broken.")]


def test_markdown_cells_preserve_table_with_pipes_and_multiline_text():
    result = auditor.render_markdown("example", [
        (auditor.WARN, "Title | text", "First | second\r\n<script>x</script>"),
    ], 50, "F")
    row = next(line for line in result.splitlines() if "Title" in line)
    assert r"Title \| text" in row
    assert r"First \| second<br>&lt;script&gt;x&lt;/script&gt;" in row
