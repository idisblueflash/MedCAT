# BDD Features (behave)

This directory holds the Behaviour-Driven Development (BDD) suite for MedCAT,
driven by [`behave`](https://behave.readthedocs.io/). It is the executable
counterpart to the specifications in [`../user-stories/`](../user-stories):
each user story is written as `Given / when / then` acceptance criteria, which
translate directly into Gherkin scenarios here.

## Layout

```
features/
├── README.md                        # this file
├── environment.py                   # behave hooks (skips @wip scenarios)
├── steps/                           # step definitions (Python)
│   └── annotation_output_steps.py   # steps for the US 09 example
└── us-09-structured-annotation-output.feature
```

- **`*.feature`** — one file per user story, named `us-NN-*.feature` to mirror
  `user-stories/us-NN-*.md`. The `Feature:` block reuses the story's
  `As a … I want … so that …` statement; each `Scenario` is one acceptance
  criterion.
- **`steps/`** — the Python glue that makes each `Given/When/Then` line
  executable against MedCAT.
- **`environment.py`** — shared hooks. It skips any feature or scenario tagged
  `@wip`, so the suite stays green while step definitions are still being
  written.

## Running

```bash
uv sync --group dev            # installs behave (and the other dev deps)
uv run behave                  # runs the suite from the repo root
uv run behave --tags=-wip      # run only implemented (non-WIP) scenarios
uv run behave features/us-09-structured-annotation-output.feature   # a single story
```

## Adding a story

1. Copy an existing `user-stories/us-NN-*.md`'s acceptance criteria into a new
   `features/us-NN-*.feature`, one `Scenario` per criterion.
2. Tag the feature `@wip` until its steps exist.
3. Implement the matching `@given/@when/@then` steps under `steps/`.
4. Remove the `@wip` tag once the scenarios pass.

The `us-09-structured-annotation-output.feature` file is a worked example of
steps 1–2 and the step stubs in `steps/annotation_output_steps.py` show the
intended pattern for step 3.
