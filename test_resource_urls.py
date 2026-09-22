import pytest

from auditor import PageParser


@pytest.mark.parametrize("html", [
    '<a href="http://example.com">Visit</a>',
    '<link rel="canonical" href="http://example.com">',
    '<meta property="og:url" content="http://example.com">',
    '<div data-example="http://example.com">Example</div>',
])
def test_navigation_and_metadata_do_not_count_as_loaded_resources(html):
    parser = PageParser()
    parser.feed(html)
    assert parser.mixed == 0


@pytest.mark.parametrize("html", [
    '<img src="http://example.com/image.png">',
    '<script src="http://example.com/app.js"></script>',
    '<iframe src="http://example.com/embed"></iframe>',
    '<link rel="alternate STYLESHEET" href=" HTTP://example.com/style.css ">',
    '<video poster="http://example.com/poster.png"></video>',
    '<object data="http://example.com/document"></object>',
])
def test_insecure_resource_attributes_are_still_counted(html):
    parser = PageParser()
    parser.feed(html)
    assert parser.mixed == 1


def test_secure_resource_is_not_flagged():
    parser = PageParser()
    parser.feed('<img src="https://example.com/image.png">')
    assert parser.mixed == 0
