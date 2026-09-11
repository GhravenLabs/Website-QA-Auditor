# Reviewer Quickstart

Website QA Auditor is a zero-dependency Python CLI for launch-readiness checks.

## Suggested review path

1. Read `README.md` for supported checks and example usage.
2. Inspect `auditor.py` for parsing, rule evaluation, and report output.
3. Review `sample.html` and `sample-report.md` for expected report style.
4. Run tests before changing scoring or findings.

## Local verification

```bash
python -m pytest
python auditor.py --file sample.html --out sample-report.md
```

The tool should keep working without optional AI summary support and should avoid requiring third-party packages for the main audit path.

