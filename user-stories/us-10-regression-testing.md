# US 10 Regression Testing Across Model and Ontology Versions

This specification describes how MedCAT verifies that a newly built model pack still behaves acceptably compared to expectations when the underlying ontology (e.g. SNOMED-CT) has moved to a new release.

## Core Purpose

`medcat/utils/regression/regression_checker.py` runs a YAML-defined suite of patient-record templates containing placeholders (e.g. `[FINDING1]`, `[FINDING2]`, `[DISORDER]`), each mapped to a specific expected CUI and name, against a target model pack via `python -m medcat.utils.regression.regression_checker <model pack> [suite yaml]`. It reports how many (sub)cases matched expectations and how many didn't.

## Key Design Consideration

Rather than a binary pass/fail, results are graded at configurable strictness levels (`IDENTICAL`, `BIGGER_SPAN_LEFT`/`RIGHT`/`BOTH`, `SMALLER_SPAN`, `FOUND_ANY_CHILD`, `FOUND_CHILD_PARTIAL`, `PARTIAL_OVERLAP`, `FAIL`). This distinguishes a genuine regression from an expected side effect of an ontology upgrade — for example, a new model correctly linking to a more specific child concept, or shifting a span boundary slightly — which would otherwise drown real failures in noise.

## Acceptance Criteria Summary

The specification requires:
- A default suite (`configs/default_regression_tests.yml`) runs out of the box without requiring a custom YAML
- Results report per-case and aggregate counts and percentages at the configured strictness level
- Failing (sub)cases print the offending phrase, placeholder, expected CUI, and expected name so a developer can triage without re-running the suite under a debugger
- Placeholders can each be checked against many candidate names/CUIs, not just a single hardcoded expectation

## Implementation Notes

Placeholder resolution lives in `targeting.py`, outcome grading against strictness levels in `checking.py`, and result aggregation in `results.py`, all under `medcat/utils/regression/`. See `medcat/utils/regression/README.md` for the full walkthrough and example output.
