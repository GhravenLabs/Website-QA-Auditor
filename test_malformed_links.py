from contextlib import nullcontext
from types import SimpleNamespace

import pytest

import auditor


@pytest.mark.parametrize('invalid', ['http://[broken', 'https://[not-an-ip]/'])
def test_malformed_href_is_reported_and_remaining_links_checked(monkeypatch, invalid):
    requested = []

    def open_link(request, **kwargs):
        requested.append(request.full_url)
        return nullcontext(SimpleNamespace(status=200))

    monkeypatch.setattr(auditor.urllib.request, 'urlopen', open_link)
    rows = auditor.check_links([invalid, invalid, '/valid'], 'https://example.com')
    assert requested == ['https://example.com/valid']
    assert rows == [(auditor.FAIL, 'Broken link', f'ValueError {invalid}')]


def test_malformed_urls_respect_check_budget(monkeypatch):
    def no_network(*args, **kwargs):
        pytest.fail('budget should be exhausted by the malformed link')

    monkeypatch.setattr(auditor.urllib.request, 'urlopen', no_network)
    rows = auditor.check_links(['http://[bad', '/valid'], 'https://example.com', cap=1)
    assert len(rows) == 1
    assert rows[0][0] == auditor.FAIL
