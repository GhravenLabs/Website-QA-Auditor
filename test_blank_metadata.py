from auditor import PageParser, audit

def test_blank_metadata_does_not_pass_presence_checks():
    p = PageParser()
    p.feed('<html lang="  "><meta name="viewport" content=" "><meta name="description" content=" "><meta property="og:title" content=" ">')
    checks = {check: severity for severity, check, _ in audit(p, 100)}
    assert checks["Mobile viewport"] == "FAIL"
    assert checks["Language attribute"] == "WARN"
    assert checks["Meta description"] == "FAIL"
    assert p.metas["og:title"] == ""
