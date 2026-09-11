# Audit Rules Checklist

Use this checklist before adding or changing website audit rules.

## Rule quality

- The finding is specific and fixable.
- The reason is written in plain English.
- The rule avoids false confidence when markup is missing or malformed.
- Severity matches the practical impact.

## Verification

- Add or update a sample fixture when behavior changes.
- Keep report output stable enough for reviewers to compare.
- Confirm `--file` mode works without network access.
- Keep optional live link checks clearly optional.

