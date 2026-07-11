# Rule 08 — Change workflow (per change)

**Every code change runs the same phased loop: sync `main` → orient in the real
module → strict red/green (Rule 02) → clear the four gates (Rule 01) → guard
serialization & deprecation (Rules 03–04) → self-review → chunked commits →
second-opinion review → PR against `main`.** Each phase ends at a natural
checkpoint; do not skip ahead. This is paper-degist's Rule 06 process, retuned to
MedCAT's library reality (no BDD, no CLI-pipeline, no per-story branch ceremony —
but the same test-first, gate-guarded, two-review spine).

## The phases

### 1. Orient — read before writing
- **Sync `main` first:** `git switch main && git pull --ff-only` before branching,
  so the branch starts from the real remote tip. CONTRIBUTING requires changes be
  based on current `main`.
- Find the module you are changing under `medcat/` and read its **nearest sibling**
  for conventions (module shape, how config is threaded, how the class is
  (de)serialized). If a user story documents this behavior, open that one US file
  (Rule 05) — its AC is the contract you must not break.

### 2. TDD loop — one behavior at a time (Rule 02)
Pure logic first, then the orchestrator. Per fact: one failing test → confirm it
fails for the right reason → smallest change to green → refactor → next. Put slow
model loading in `setUpClass`.

### 3. Guard the artifact and the surface (Rules 03–04)
- If you touched `CDB`/`Vocab`/`Config`/model-pack (de)serialization, add a
  round-trip test **and** run `check_backwards_compatibility.sh` (Rule 03).
- If you are removing/renaming a public callable, deprecate it — don't delete it
  (Rule 04).

### 4. Clear the four gates (Rule 01) — before review
Run all, from repo root, and get them green:
`python -m mypy --follow-imports=normal medcat` · `flake8 medcat` · `darglint` ·
`python -m unittest discover` · plus the pydantic-1 grep. Match the CI so nothing
surfaces only after pushing.

### 5. Self-review — `/code-review`
Fan out finder angles → verify each survivor against the code → fix the real
findings **test-first**. Anchor any `file:line` finding per Rule 07.

### 6. Commit in logical, each-green chunks
Feature branch off a **remote-synced** `main`; never commit to `main` directly.
Separate a self-contained refactor from the feature so each commit passes on its
own. Do not hand-edit versions — `setuptools_scm` derives them from tags.

### 7. Second-opinion review — Codex
Hand the branch diff to Codex; fix its findings **test-first**; re-run the four
gates.

### 8. Ship
Push and open the PR against `main` with a body stating the **review trail**, the
gate results, and any deferred follow-ups. If the change deprecated anything, name
the `removal_version`. After merge, sync local `main` (`git switch main && git
pull --ff-only`) and delete the merged branch (`git branch -d`).

## Why

MedCAT's value is that a model trained and a pipeline written against it keep
working across versions and Python releases. That only holds if every change is
added the same way: tests before code (so the suite locates regressions), the four
gates green (so types/lint/docs/pydantic don't rot), serialization and the public
surface guarded (Rules 03–04, so nobody's model or import breaks), and two review
passes before merge (so plausible-but-wrong code doesn't land). The invariant
threaded through every phase: **a change that would break a downstream user is
caught by a gate or a deprecation window — never shipped as a surprise.**
