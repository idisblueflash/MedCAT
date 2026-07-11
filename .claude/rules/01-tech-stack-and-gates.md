# Rule 01 — Tech stack & the four pre-PR gates

**Python + setuptools + `unittest`, guarded by mypy, flake8, darglint, and a
pydantic-1 compatibility check. Every change clears all four gates before a PR.**

This is the MedCAT-tailored version of paper-degist's Rule 01. The grain is the
same — nothing merges until the automated checks are green — but the toolchain is
MedCAT's own, not `uv`/`behave`.

## Stack

- **Language:** Python, `python_requires='>=3.9'`. The CI matrix runs 3.9–3.12
  (`.github/workflows/main.yml`), so nothing may use syntax or stdlib newer than
  3.9.
- **Packaging:** `setuptools` + `setuptools_scm` (version derived from git tags —
  never hand-edit a version). Runtime deps live in `install_requires.txt`; dev
  deps in `requirements-dev.txt`. Install with
  `pip install -r requirements-dev.txt`. There is **no `uv`, no `pyproject`
  dependency table, no `requirements.txt` pinning** — add a runtime dep by
  editing `install_requires.txt` and a package to the `packages=[...]` list in
  `setup.py` if you add a new subpackage.
- **Pydantic:** the config layer must stay **pydantic-1 compatible**. Do not
  introduce `.dict()` or `.__fields__` without the
  `# 4pydantic1 - backwards compatibility` annotation the CI grep looks for.

## The four gates (run in this order, all from the repo root)

1. **Types** — `python -m mypy --follow-imports=normal medcat`
2. **Lint** — `flake8 medcat` (config in `.flake8`)
3. **Docstrings** — `darglint` (params/returns must match the signature)
4. **Tests** — `python -m unittest discover`

Plus the pydantic-1 grep the CI enforces:
`grep "\.dict(\|\.__fields__" medcat -rI | grep -v "# 4pydantic1"` must be empty.

## Why

MedCAT ships as a library other people pin their pipelines to, across four Python
versions and two pydantic majors. The gates are what keep a change from breaking
a downstream user silently: types catch interface drift, flake8/darglint keep the
public surface documented, and the pydantic grep keeps the config loadable under
both majors. A PR that has not cleared all four locally will fail CI — run them
before pushing, not after.
