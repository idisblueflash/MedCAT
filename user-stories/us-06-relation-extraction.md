# US 06 Relation Extraction Between Linked Concepts

As an *NLP engineer*, I want to *predict relationships between pairs of already-linked concepts*, so that *I can connect, for example, a finding to the body site it affects rather than storing isolated entities*.

`RelCAT` (`medcat/rel_cat.py`) trains and runs a transformer-based classifier over candidate pairs of linked entity spans within a document, predicting whether — and what kind of — relation connects them. It supports multiple transformer backbones through `medcat/utils/relation_extraction/`.

RelCAT operates strictly downstream of NER+L: it draws candidate pairs from CDB-linked spans rather than re-detecting entities, so relation quality is bounded by the upstream linking. Because relation classes in clinical text are heavily imbalanced (most pairs are unrelated), training uses `compute_class_weight` and a class-aware split (`split_list_train_test_by_class`) rather than a naive random split.

## Acceptance Criteria

1. Given a document already processed by the NER+L pipeline
   - when RelCAT selects candidates
     - then candidate pairs are drawn from the existing linked spans, not re-detected
2. Given a training set where most pairs are unrelated
   - when RelCAT trains
     - then class imbalance is compensated for via computed class weights
3. Given the training set is split into train/test
   - when the split is made
     - then relation-class proportions are preserved rather than split purely at random
4. Given a trained RelCAT
   - when `save_state` / `save_results` then `load_state` / `load_results` are called
     - then training state and results round-trip so a run can resume or be evaluated later

## Case handling (pairwise classification over linked spans)

The candidate pool is the set of linked-entity pairs in a document; each pair is classified into a relation type or "no relation". Configuration lives in `medcat/config_rel_cat.py`; model-specific components under `medcat/utils/relation_extraction/`. Coverage lives in `tests/test_rel_cat.py`.

## Later stages (deferred)

- **Candidate pruning.** All in-document pairs are considered; distance- or type-based pruning would cut the quadratic candidate count on long notes.
- **Cross-sentence relations.** Focus is within-document pairs; explicit handling of long-range or cross-section relations is left open.
