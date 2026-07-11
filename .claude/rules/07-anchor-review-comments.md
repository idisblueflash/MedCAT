# Rule 07 — Anchor review findings to the diff line

**When a code-review finding names a specific `file:line`, post it as an inline
review comment on that line — not as a PR-level (issue) comment that only mentions
the location in prose.** Carried over from paper-degist's Rule 04; it is
tool-agnostic and applies unchanged here.

## The principle

A finding read next to the code it describes needs no hunting: the reader sees the
line and "this `.dict()` call breaks pydantic-1 load" together. The same text in
the PR comment stream forces the reader to open the file and scroll to the line.
The review tool (`/code-review`, Codex, a human) has already computed the anchor —
posting inline puts the comment where the anchor points instead of describing it
in words. Inline comments also resolve, collapse, and travel with the code.

## Classify-then-dispatch

- **Has `file:line` in the PR diff at the current head SHA** → inline review
  comment (`path`, `line`, `side: RIGHT`, `commit_id: <head sha>`).
- **Anchor is stale or outside the diff** (line drifted since the review ran, or
  points at unchanged context GitHub won't accept) → quarantine to a PR-level
  comment and say the anchor did not resolve. Never force an inline comment onto
  the wrong line.
- **No single line** (overall verdict, cross-cutting concern like "this breaks
  model backwards-compat across the module") → PR-level comment by design.

Verify each anchor against `gh pr diff` before posting; don't trust line numbers
from a review that ran against a local tree differing from the pushed diff. Post
each finding independently and capture per-comment success/failure, so one
rejected anchor quarantines itself without dropping the rest of the batch.

## Why

A review is only as useful as it is easy to act on. Findings stranded in the
comment stream get skimmed and lost; findings pinned to the line get fixed. The
classify-then-dispatch split keeps the anchoring honest — a comment lands on the
diff only when the diff actually contains the cited line, and everything else is
named as unanchored rather than faked onto a wrong location.
