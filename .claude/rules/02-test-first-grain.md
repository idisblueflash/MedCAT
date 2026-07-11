# Rule 02 — Test-first, one behavior per test (unittest grain)

**Each test asserts one logical fact, and each new behavior is driven by a
failing test written before the production code. No bulk-writing tests and
implementing against all of them at once.** This is paper-degist Rules 01+05
rendered in MedCAT's `unittest` idiom.

## The two disciplines

### One logical fact per test method

A test method fails for exactly one reason, and its name states that reason
(`test_prepare_csvs_merges_rows_sharing_cui`, not `test_cdb_maker`). Split any
test whose assertions are causally independent (control-flow vs. data-shape:
"malformed rows are reported" is one test; "names survive the save/load round
trip" is another). "One fact" is logical, not literal — asserting a whole record
equals an expected dict is one fact.

- Factor shared arrange/act into `setUp`, `setUpClass`, or a private helper, so
  the split never duplicates fixtures. `tests/test_cdb.py` already does this
  (`setUpClass` builds the `CDBMaker`, `setUp` resets and re-prepares the CDB) —
  copy that shape rather than rebuilding a spaCy model per test.
- Prefer `subTest` for a genuine table of same-shape cases over pasting a loop's
  worth of near-identical asserts.

### Strict red → green → refactor, one at a time

Write **one** failing test, run it (`python -m unittest tests.test_x.Class.method`),
confirm it fails for the right reason, make it pass with the smallest change,
refactor, then write the next. Do not write many tests up front and implement in
one pass — that forfeits triangulation (a next-test-already-green signals the
behavior is covered, so drop the redundant test) and design emergence (the
interface is driven by the tests, not retrofitted to code).

## Where tests live

- Tests are `tests/test_<module>.py`, `unittest.TestCase` subclasses. New
  behavior in `medcat/x.py` is tested in `tests/test_x.py`.
- Sample inputs live under `examples/` and `tests/resources/` — reuse the
  existing `examples/cdb.csv` / `vocab.dat` fixtures; do not scatter new ad-hoc
  data files (see Rule 06).
- Anything that loads a spaCy model or trains is **slow** — keep it in
  `setUpClass`, and keep genuinely fast unit logic free of model loading so the
  suite stays runnable.

## Why

The suite's job is to *locate* a regression, not merely detect one. One fact per
test plus one-test-at-a-time construction means every red test points at a single
behavior and the suite carries no dead weight — each test earned its place by
failing before the code that satisfied it existed. This matters more in MedCAT
than in a fresh pipeline, because the tests double as the executable spec for a
library other people depend on.
