# MedCAT working rules

Project-specific rules for how changes get made in this repo. They are adapted
from [paper-degist's rules](https://github.com/idisblueflash/paper-degist/tree/master/.claude/rules)
but retuned to MedCAT's real reality: a versioned, pip-installed clinical-NLP
**library** whose serialized models and public API are downstream users'
dependencies — not a greenfield CLI pipeline.

Each rule follows the same shape: **principle → in practice → why**, and
cross-links the others by number.

| # | Rule | In one line |
| --- | --- | --- |
| [01](01-tech-stack-and-gates.md) | Tech stack & the four pre-PR gates | setuptools + `unittest`, guarded by mypy · flake8 · darglint · pydantic-1 grep. |
| [02](02-test-first-grain.md) | Test-first, one behavior per test | `unittest` grain: one logical fact per method, strict red→green, one at a time. |
| [03](03-backwards-compatibility.md) | Serialized artifacts stay compatible | Old CDB/Vocab/Config/model packs must still load; round-trip is a test. |
| [04](04-deprecate-dont-delete.md) | Deprecate on a schedule | `@deprecated` + `check_deprecations.py` — never delete the public surface abruptly. |
| [05](05-one-file-per-user-story.md) | One file per user story, indexed | `user-stories.md` is the map; each `us-NN-*.md` is one story, faithful to real code. |
| [06](06-distinct-example-data.md) | Distinct, meaningful example data | Every same-kind value (CUI, name, path) is different and self-describing. |
| [07](07-anchor-review-comments.md) | Anchor review findings to the line | `file:line` findings post inline; stale/no-anchor ones quarantine to PR-level. |
| [08](08-change-workflow.md) | Change workflow (per change) | The phased loop tying 01–07 together, from `git pull` to PR against `main`. |

## Not carried over from paper-degist

- **CLI-runnable-per-step** — MedCAT is an imported library, not a step-per-CLI
  pipeline, so there is no console-script contract to uphold.
- **Remote dev on a second machine** — operator/infra-specific, not a property of
  this repo.

Rules 03 and 04 are new here: they capture what most distinguishes MedCAT from a
fresh pipeline — it is a versioned library, so its serialized models and public
API must not break underneath the people who depend on them.
