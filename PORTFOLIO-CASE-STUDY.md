# Portfolio Case Study: Website QA Auditor

## Problem
Small business websites often launch with missing metadata, weak heading structure, image alt gaps, broken links, social-preview problems, and pages that are hard for AI answer engines to understand. These are fixable, but owners usually do not know what to check.

## Build
Website QA Auditor is a zero-dependency Python CLI that audits local files or live URLs, scores the page, prints terminal findings, and writes a client-ready Markdown report. The latest pass adds AI-search readiness checks for canonical URLs, indexability, JSON-LD structured data, and plain-text service/contact/FAQ signals.

## Why it is useful
- Turns a fuzzy "your website needs work" pitch into a concrete report.
- Supports Webloom-style website QA, deployment rescue, and launch-readiness offers.
- Connects normal SEO/a11y checks to the newer AI-search/GEO problem: can answer engines identify who the page is for and what the business offers?
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
