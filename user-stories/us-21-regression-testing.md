# US 21 Regression Testing Across Model and Ontology Versions

As a *model maintainer*, I want to *check a newly built model pack against a set of expected concept results*, so that *I can tell a real regression apart from an expected effect of upgrading an ontology (like SNOMED-CT), before I ship the new model*.

("Regression" here means the model getting worse at something it used to do right. A "regression test" checks for exactly that.)

`medcat/utils/regression/regression_checker.py` runs a test suite written in YAML — a file listing template patient-record sentences with placeholders like `[FINDING1]` or `[DISORDER]`, each one mapped to the concept code and name it's expected to resolve to. You run it against a model pack with:
`python -m medcat.utils.regression.regression_checker <model pack> [suite yaml]`
and it reports how many cases matched, and how many didn't.

Instead of a simple pass/fail, each result gets graded at one of several strictness levels: `IDENTICAL`, `BIGGER_SPAN_LEFT`/`RIGHT`/`BOTH`, `SMALLER_SPAN`, `FOUND_ANY_CHILD`, `FOUND_CHILD_PARTIAL`, `PARTIAL_OVERLAP`, `FAIL`. This matters because an ontology upgrade can legitimately change a result without it being a mistake — for example, a new model correctly linking to a more specific "child" concept, or a match's boundary shifting slightly. Without these grading levels, changes like that would look like failures and bury the real, meaningful ones.

## Acceptance Criteria

1. Given no custom test suite is supplied
   - when the checker runs
     - then the built-in default suite (`configs/default_regression_tests.yml`) runs right out of the box
2. Given a suite has finished running against a model pack
   - when results are reported
     - then per-case and overall counts and percentages are shown, at whichever strictness level was configured
3. Given a test case fails
   - when the results are printed
     - then the specific phrase, placeholder, expected concept code, and expected name are all shown, so a developer can figure out what went wrong without needing a debugger
4. Given a placeholder has more than one acceptable answer
   - when the suite is written
     - then it can be checked against several candidate names/concept codes, instead of just one hardcoded expected answer

## Case handling (fill in placeholders, grade by strictness, then combine)

Each placeholder in a template is filled in, the model's output is compared to the expected result at the chosen strictness level, and the outcomes are combined into a summary. Filling in placeholders happens in `targeting.py`, grading happens in `checking.py`, and combining results happens in `results.py` — all under `medcat/utils/regression/`. See `medcat/utils/regression/README.md` for a full walkthrough with example output.

## Later stages (deferred)

- **No automatic CI gate.** The checker reports counts, but nothing currently fails a build automatically when a real regression is detected. Wiring a strictness threshold into CI would do that.
- **No auto-generated test suites.** Templates are currently written by hand. Automatically deriving test cases from a MedCATtrainer export would widen coverage with less manual work.
