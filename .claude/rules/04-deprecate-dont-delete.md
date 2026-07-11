# Rule 04 — Deprecate on a schedule; never delete the public surface abruptly

**A public function or method is removed in two steps across releases: first mark
it `@deprecated` with the version it dies in, then remove it only once that
version arrives. The removal is enforced by tooling, not memory.**

## The principle

MedCAT is imported by pipelines the maintainers do not control. Deleting a public
name in a patch release breaks those callers with no warning. The repo already
encodes the humane path: `medcat/utils/decorators.py` provides
`@deprecated(message, depr_version, removal_version)`, and
`tests/check_deprecations.py` scans for decorated functions whose `removal_version`
has arrived — so removals happen *on schedule* and are impossible to forget.

## In practice

- **Removing/renaming a public callable** → don't delete it. Decorate the old one:
  ```python
  @deprecated("Use CDB.load instead.", depr_version=(1, 16, 0), removal_version=(2, 0, 0))
  def old_load(...): ...
  ```
  Keep it forwarding to the replacement until `removal_version` lands.
- **Actually removing** happens only in the release named by `removal_version`,
  driven by `python tests/check_deprecations.py <version> --next-version
  --remove-prefix` (the CI runs this on the `production` PR just before a
  release) — not opportunistically mid-cycle.
- **Changing behavior, not just the name:** if callers relied on the old
  behavior, that is also a deprecation, not a silent swap — deprecate the old
  path and introduce the new one alongside.
- **Internal (underscore-prefixed) helpers** are exempt — this rule guards the
  *public* surface real users import.

## Why

The point is the same as paper-degist's "unknowns go to the manifest, Claude
re-enters once": a change that would break a caller is *quarantined* into a
deprecation window instead of dropped on them. The window is tracked in code
(`@deprecated` + `check_deprecations.py`), so the eventual removal is deliberate
and scheduled rather than a surprise in someone's production pipeline.
