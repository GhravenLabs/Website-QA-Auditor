import pytest
from auditor import PageParser, audit

@pytest.mark.parametrize("content, expected", [("NONE", "FAIL"), ("follow, noindex", "FAIL"), ("notnoindex", "PASS"), ("index, follow", "PASS")])
def test_robots_tokens(content, expected):
    p = PageParser()
    p.feed(f'<meta name="robots" content="{content}">')
    assert next(severity for severity, check, _ in audit(p, 100) if check == "Indexability") == expected


@pytest.mark.parametrize("contents, expected", [
    (["noindex", "follow"], "FAIL"),
    (["NONE", "index, follow"], "FAIL"),
    (["noindex", ""], "FAIL"),
    (["follow", "noindex"], "FAIL"),
    (["index", "follow"], "PASS"),
])
def test_multiple_robots_tags_preserve_restrictive_directives(contents, expected):
    p = PageParser()
    for content in contents:
        p.feed(f'<meta name="robots" content="{content}">')
    assert next(severity for severity, check, _ in audit(p, 100)
                if check == "Indexability") == expected
