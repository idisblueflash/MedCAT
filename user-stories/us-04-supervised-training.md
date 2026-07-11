# US 04 Supervised Fine-Tuning from Annotated Trainer Exports

This specification describes how human review corrections, captured in MedCATtrainer, feed back into the model to fix linking mistakes that unsupervised training cannot.

## Core Purpose

`CAT.train_supervised_from_json` and `CAT.train_supervised_raw` (`medcat/cat.py:803,841`) consume a MedCATtrainer JSON export containing human-reviewed annotations — each marked correct, incorrect, or given an alternative CUI — and use them to reinforce correct context vectors and penalise incorrect ones.

## Key Design Consideration

Annotations flagged `irrelevant` are collected per-project (`get_all_irrelevant_cuis`, `medcat/utils/filters.py`) specifically to identify CUIs the model should stop suggesting in that context, acting as a guardrail against a reviewer's corrections silently reinforcing the same bad link elsewhere in the document set. Long supervised runs can also checkpoint mid-training via `medcat/utils/checkpoint.py` (`Checkpoint.save` / `restore_latest_cdb`), so a failure partway through a large export doesn't discard already-applied corrections.

## Acceptance Criteria Summary

The specification requires:
- Annotations marked correct reinforce the existing CUI-name link
- Annotations marked incorrect or reassigned to an alternative CUI adjust the model away from the wrong link
- Training can resume from the last checkpoint after an interruption instead of restarting from scratch
- The trainer export format (documents containing per-annotation CUI, span, and correctness flags) is the same one produced by the MedCATtrainer web application

## Implementation Notes

This workflow is designed to close the loop with [MedCATtrainer](https://github.com/CogStack/MedCATtrainer), the companion annotation UI: a reviewer corrects model output there, exports the project as JSON, and that export is fed straight into `train_supervised_from_json`. Coverage lives in `tests/test_entity_linking.py`.
