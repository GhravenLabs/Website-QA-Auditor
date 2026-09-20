import pytest
from auditor import PageParser, audit

@pytest.mark.parametrize("content, expected", [("NONE", "FAIL"), ("follow, noindex", "FAIL"), ("notnoindex", "PASS"), ("index, follow", "PASS")])
def test_robots_tokens(content, expected):
    p = PageParser()
    p.feed(f'<meta name="robots" content="{content}">')
    assert next(severity for severity, check, _ in audit(p, 100) if check == "Indexability") == expected
