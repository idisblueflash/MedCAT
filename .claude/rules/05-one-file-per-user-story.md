# Rule 05 — One file per user story, indexed

**Each user story lives in its own file under `user-stories/`, and
[`user-stories.md`](../../user-stories.md) is the index that maps every US to its
file, its pipeline stage, and a one-line description. Navigate to the one story in
play via the index — never read the whole spec to find it.** This codifies the
convention MedCAT already adopted from paper-degist's Rule 07.

## The shape (as already built here)

- **`user-stories.md`** is the **index only**: the one-paragraph architectural
  summary plus tables grouped by stage (**build a model → annotate a document →
  train → layer on top → operate**), one row per US — number linked to its file,
  title, and a short description. It carries no acceptance criteria.
- **`user-stories/us-NN-<slug>.md`** holds one story: the `# US NN Title`
  heading, the "As a … I want … so that …" statement, a short prose orientation
  naming the real `medcat/` entry point it documents (e.g.
  `CDBMaker.prepare_csvs` in `medcat/cdb_maker.py`), its `## Acceptance Criteria`
  in Given/When/Then form, and optional `## Case handling` / `## Later stages
  (deferred)` sections. `NN` is zero-padded so the directory sorts in story order.

## MedCAT specifics

- **These stories are reverse-engineered from real code**, not a greenfield
  backlog. Each US must name and stay faithful to the actual module/class/method
  it describes — the AC are the observable contract of existing code, so verify
  against `medcat/` before writing or editing one.
- **The pipeline ordering is load-bearing.** The annotation-stage stories are
  ordered to follow the pipeline as it runs (normalise → detect → disambiguate →
  resolve overlaps → restrict → output). Keep new annotation stories in that
  running order, not in numeric order of creation.

## Adding or changing a story

- **New US** → create `user-stories/us-NN-<slug>.md` (copy a sibling's shape) and
  add its row to the correct stage table in the index. Do both in one change.
- **Renaming/renumbering** → keep the file's `NN` slug and the index row in
  lockstep, and fix any `[US NN](user-stories/…)` links.

## Why

The spec is only useful if the *relevant* story is cheap to find and safe to edit
in isolation. The index holds the whole map in one glance (what exists, what
stage, what it documents) while each file stays self-contained — so a task
touching US 06 opens `us-06-disambiguating-a-mention-by-context.md` alone, with no
unrelated ACs and no accidental edits to a neighbouring story.
