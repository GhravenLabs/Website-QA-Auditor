# Portfolio Case Study: Website QA Auditor

## Problem
Small business websites often launch with missing metadata, weak heading structure, image alt gaps, broken links, and social-preview problems. These are fixable, but owners usually do not know what to check.

## Build
Website QA Auditor is a zero-dependency Python CLI that audits local files or live URLs, scores the page, prints terminal findings, and writes a client-ready Markdown report.

## Why it is useful
- Turns a fuzzy "your website needs work" pitch into a concrete report.
- Supports Webloom-style website QA, deployment rescue, and launch-readiness offers.
- Runs with the Python standard library only, so clients or reviewers can reproduce it easily.
- The sample report can be used as outreach proof before asking for access.

## Verification
- Sample terminal proof: `assets/screenshot.png`
- Sample reports: `sample-report.md` and `medspa-qa-report.md`
- Smoke check: `.github/workflows/smoke.yml`

## Next upgrades
- Add JSON output for dashboards and lead scoring.
- Add a small web wrapper so non-technical users can paste a URL.
- Add Lighthouse/API integration as an optional deeper audit tier.
