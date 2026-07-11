# US 21 Regression Testing Across Model and Ontology Versions

As a *model maintainer*, I want to *check a newly built model pack against expected concept results*, so that *I can tell a genuine regression from an expected effect of an ontology (e.g. SNOMED-CT) upgrade before I ship*.

`medcat/utils/regression/regression_checker.py` runs a YAML-defined suite of patient-record templates containing placeholders (e.g. `[FINDING1]`, `[DISORDER]`), each mapped to an expected CUI and name, against a target model pack via `python -m medcat.utils.regression.regression_checker <model pack> [suite yaml]`, and reports how many (sub)cases matched and how many didn't.

Rather than binary pass/fail, results are graded at configurable strictness levels (`IDENTICAL`, `BIGGER_SPAN_LEFT`/`RIGHT`/`BOTH`, `SMALLER_SPAN`, `FOUND_ANY_CHILD`, `FOUND_CHILD_PARTIAL`, `PARTIAL_OVERLAP`, `FAIL`). This distinguishes a real regression from an expected upgrade side effect — a new model correctly linking to a more specific child concept, or shifting a span boundary slightly — which would otherwise drown real failures in noise.

## Acceptance Criteria

1. Given no custom suite is supplied
   - when the checker runs
     - then the default suite (`configs/default_regression_tests.yml`) runs out of the box
2. Given a suite has run against a model pack
   - when results are reported
     - then per-case and aggregate counts and percentages are shown at the configured strictness level
3. Given a (sub)case fails
   - when results are printed
     - then the offending phrase, placeholder, expected CUI, and expected name are shown so a developer can triage without a debugger
4. Given a placeholder with several acceptable resolutions
   - when the suite is defined
     - then it can be checked against many candidate names/CUIs, not a single hardcoded expectation

## Case handling (grade-by-strictness)

Each placeholder is resolved, the model's output is graded against the expected result at the chosen strictness level, and outcomes are aggregated. Placeholder resolution lives in `targeting.py`, grading in `checking.py`, and aggregation in `results.py`, all under `medcat/utils/regression/`. See `medcat/utils/regression/README.md` for a full walkthrough and example output.

## Later stages (deferred)

- **CI gating.** The checker reports counts; wiring a strictness/threshold gate into CI would fail a build automatically on real regressions.
- **Auto-generated suites.** Templates are authored by hand; deriving candidate cases from a trainer export would broaden coverage with less manual effort.
