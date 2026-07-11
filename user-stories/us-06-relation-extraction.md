# US 06 Relation Extraction Between Linked Concepts

This specification describes how MedCAT identifies relationships between pairs of already-linked concepts within a document, such as connecting a finding to the body site it affects.

## Core Purpose

`RelCAT` (`medcat/rel_cat.py`) trains and runs a transformer-based classifier over candidate pairs of linked entity spans within a document, predicting whether — and what kind of — relation connects them. It supports multiple transformer backbones through `medcat/utils/relation_extraction/`.

## Key Design Consideration

RelCAT operates strictly downstream of NER+L: it takes CDB-linked entity spans as its candidate pool rather than re-detecting entities itself, so relation quality is bounded by the quality of the upstream linking step. Because relation classes in clinical text are typically heavily imbalanced (most entity pairs are unrelated), training uses `compute_class_weight` and a class-aware train/test split (`split_list_train_test_by_class`) rather than a naive random split.

## Acceptance Criteria Summary

The specification requires:
- Candidate entity pairs are drawn from spans already produced by the NER+L pipeline
- Class imbalance between related and unrelated pairs is explicitly compensated for during training
- Train/test splitting preserves relation-class proportions rather than splitting purely randomly
- Training state and results can be persisted (`save_state`, `save_results`) and reloaded (`load_state`, `load_results`) to resume or evaluate later

## Implementation Notes

Configuration lives in `medcat/config_rel_cat.py`; model-specific components live under `medcat/utils/relation_extraction/`. Coverage lives in `tests/test_rel_cat.py`.
