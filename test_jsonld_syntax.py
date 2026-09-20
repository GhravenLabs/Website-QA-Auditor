import pytest
from auditor import PageParser

@pytest.mark.parametrize("mime, data, expected", [("application/ld+json", "broken", 0), ("application/ld+json", "42", 0), ("application/ld+json", '{"@type":"Organization"}', 1), ("application/ld+json", "[]", 1), ("text/ld+json-fake", "{}", 0)])
def test_jsonld_requires_object_or_array(mime, data, expected):
    p = PageParser()
    p.feed(f'<script type="{mime}">{data}</script>')
    assert p.json_ld_count == expected
