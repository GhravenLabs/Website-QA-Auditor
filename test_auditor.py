from auditor import FAIL, PASS, WARN, PageParser, audit


def _rows_for(html: str):
    parser = PageParser()
    parser.feed(html)
    return audit(parser, len(html.encode("utf-8")))


def _by_check(rows):
    return {check: (severity, detail) for severity, check, detail in rows}


def test_ai_search_readiness_signals_pass_when_present():
    rows = _by_check(
        _rows_for(
            """
            <html lang="en">
              <head>
                <title>Example Accounting Automation Services</title>
                <meta name="description" content="Accounting automation services for invoice cleanup, website QA, reporting, and client-ready process documentation.">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <meta name="robots" content="index,follow">
                <link rel="canonical" href="https://example.com/services">
                <script type="application/ld+json">{"@type":"Service"}</script>
              </head>
              <body>
                <h1>Accounting automation services</h1>
                <p>Services, pricing, contact, hours, process, and FAQ answers.</p>
              </body>
            </html>
            """
        )
    )

    assert rows["Canonical URL"][0] == PASS
    assert rows["Indexability"][0] == PASS
    assert rows["Structured data"][0] == PASS
    assert rows["Answer-ready content"][0] == PASS


def test_noindex_is_a_fail_for_answer_engine_visibility():
    rows = _by_check(
        _rows_for(
            """
            <html>
              <head>
                <title>Hidden Services Page With Enough Characters</title>
                <meta name="description" content="A page with enough description text to avoid unrelated description warnings in this focused test.">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <meta name="robots" content="noindex,nofollow">
              </head>
              <body><h1>Hidden page</h1></body>
            </html>
            """
        )
    )

    assert rows["Indexability"][0] == FAIL
    assert rows["Canonical URL"][0] == WARN
