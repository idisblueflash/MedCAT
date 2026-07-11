# Rule 06 — Distinct, meaningful example data

**When more than one example, test case, or doc snippet needs a value of the same
kind (a CUI, a concept name, a CSV path), give each a *different* and
*descriptive* one — never copy-paste the same placeholder down the list.** This is
paper-degist's Rule 08, applied to MedCAT's clinical fixtures.

## The principle

Reused placeholder data reads as noise: three test cases that all annotate
`"kidney failure"` force the reader to diff long identical strings to see the
cases differ at all, and hide which value each case exercises. Distinct,
recognizable values make the doc readable at a glance and the test verbose about
its own intent — the CUI/name *is* the label for what the case is about.

## In practice

- **Unit tests.** When triangulating a behavior across cases, vary the fixture per
  case — a disambiguation test uses two genuinely different meanings of an
  ambiguous term (so the surrounding-context signal is real), not the same term
  twice. Use a preferred-name (`name_status='P'`) concept for the must-link case
  and a `name_status='N'` one for the forced-disambiguation case, so the fixture
  names the branch it tests.
- **User-story acceptance criteria.** Each Given/When/Then that takes an example
  concept picks its own, chosen so the value tells you what the scenario is about,
  while still satisfying the step's real precondition (a name that genuinely
  exists in the CDB fixture, a CUI that is actually ambiguous).
- **Example CSVs / docs (`examples/`).** The happy-path example and the
  malformed/edge example use different inputs, so the reader sees two distinct
  cases — mirror the existing `cdb.csv` vs. `complex_cdb.csv` split and keep
  `examples/README.md` describing each column.

## Why

Examples are documentation. Identical repeated values make a reader work to find
the difference and make a test mute about what it covers; distinct meaningful
values turn every example into a self-describing label. In a medical-NLP library
this is doubly true — a well-chosen CUI/name pair shows the reader *why* the case
is interesting (ambiguity, overlap, a preferred name) without a comment.
