# US 04 Supervised Fine-Tuning from Annotated Trainer Exports

As a *model maintainer*, I want to *feed human-reviewed corrections back into the model*, so that *linking mistakes unsupervised training can't fix are corrected from ground truth*.

`CAT.train_supervised_from_json` and `CAT.train_supervised_raw` (`medcat/cat.py:803,841`) consume a MedCATtrainer JSON export of human-reviewed annotations — each marked correct, incorrect, or reassigned to an alternative CUI — and use them to reinforce correct context vectors and penalise incorrect ones.

The risk is that a reviewer's corrections silently reinforce the same bad link elsewhere. Annotations flagged `irrelevant` are collected per project (`get_all_irrelevant_cuis`, `medcat/utils/filters.py`) specifically to identify CUIs the model should stop suggesting in that context. Long runs can checkpoint mid-training via `medcat/utils/checkpoint.py` (`Checkpoint.save` / `restore_latest_cdb`), so a failure partway through a large export doesn't discard already-applied corrections.

## Acceptance Criteria

1. Given an annotation marked correct
   - when supervised training runs
     - then the existing CUI-name link is reinforced
2. Given an annotation marked incorrect or reassigned to an alternative CUI
   - when supervised training runs
     - then the model is adjusted away from the wrong link
3. Given a long training run is interrupted
   - when it is restarted
     - then it resumes from the last checkpoint instead of from scratch
4. Given a project exported from the MedCATtrainer web app
   - when it is passed to `train_supervised_from_json`
     - then the export's per-annotation CUI, span, and correctness flags are consumed directly with no reformatting

## Case handling (reinforce / penalise / guard)

Each annotation is dispatched by its correctness flag: correct reinforces, incorrect/reassigned penalises, and `irrelevant` feeds the per-project guard list. The workflow closes the loop with [MedCATtrainer](https://github.com/CogStack/MedCATtrainer): a reviewer corrects model output there, exports JSON, and that export is fed straight back in. Coverage lives in `tests/test_entity_linking.py`.

## Later stages (deferred)

- **Catastrophic-forgetting checks.** There is no automatic guard that supervised passes don't degrade previously correct links; a before/after regression gate (US 10) could be wired in.
- **Active-learning selection.** Reviewers choose what to correct manually; surfacing the model's least-confident links would target review effort.
