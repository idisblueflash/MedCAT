# BDD Features (behave)

This directory holds the Behaviour-Driven Development (BDD) suite for MedCAT,
driven by [`behave`](https://behave.readthedocs.io/). It is the executable
counterpart to the specifications in [`../user-stories/`](../user-stories):
each user story is written as `Given / when / then` acceptance criteria, which
translate directly into Gherkin scenarios here.

## Layout

```
features/
├── README.md                 # this file
├── environment.py            # behave hooks (skips @wip scenarios)
├── steps/                    # step definitions (Python)
│   └── ner_linking_steps.py  # steps for the US 01 example
└── us-01-ner-and-linking.feature
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
pip install -r requirements-dev.txt   # installs behave
behave                                 # runs the suite from the repo root
behave --tags=-wip                     # run only implemented (non-WIP) scenarios
behave features/us-01-ner-and-linking.feature   # a single story
```

## Adding a story

1. Copy an existing `user-stories/us-NN-*.md`'s acceptance criteria into a new
   `features/us-NN-*.feature`, one `Scenario` per criterion.
2. Tag the feature `@wip` until its steps exist.
3. Implement the matching `@given/@when/@then` steps under `steps/`.
4. Remove the `@wip` tag once the scenarios pass.

The `us-01-ner-and-linking.feature` file is a worked example of steps 1–2 and
the step stubs in `steps/ner_linking_steps.py` show the intended pattern for
step 3.
