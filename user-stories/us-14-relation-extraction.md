# US 14 Relation Extraction Between Linked Concepts

As an *NLP engineer*, I want to *predict how two already-linked concepts relate to each other*, so that *I can connect, for example, a finding to the body part it affects, instead of storing separate, disconnected entities*.

`RelCAT` (`medcat/rel_cat.py`) trains and runs a transformer-based classifier over pairs of already-linked entity spans in a document. For each pair, it predicts whether they're related, and if so, what kind of relation connects them. It supports several different transformer models through `medcat/utils/relation_extraction/`.

RelCAT only runs *after* concept recognition and linking are done — it picks candidate pairs from concepts the CDB has already linked (US 05–07), rather than detecting entities itself. That means how good the relations are depends directly on how good the earlier linking was. Also, in real clinical text, most possible pairs of concepts are *not* related to each other — relation types are heavily imbalanced. To handle that, training uses `compute_class_weight` (to give rarer relation types more weight) and a class-aware split (`split_list_train_test_by_class`), instead of splitting the data purely at random.

## Acceptance Criteria

1. Given a document already processed by the concept-recognition-and-linking pipeline
   - when RelCAT selects candidate pairs
     - then it picks them from the already-linked spans — it does not detect any new entities itself
2. Given a training set where most pairs have no relation
   - when RelCAT trains
     - then that imbalance is compensated for using computed class weights
3. Given the training data is split into a train set and a test set
   - when the split happens
     - then the proportion of each relation type is preserved in both sets, rather than splitting purely at random
4. Given a RelCAT model has already been trained
   - when `save_state` / `save_results` are called, followed later by `load_state` / `load_results`
     - then the training progress and results come back exactly as they were, so a run can be resumed or evaluated later

## Case handling (classify every pair of linked spans)

The pool of candidates is every pair of already-linked entities found in a document; each pair gets classified as one relation type, or as "no relation." Settings live in `medcat/config_rel_cat.py`; model-specific pieces live under `medcat/utils/relation_extraction/`. Tests live in `tests/test_rel_cat.py`.

## Later stages (deferred)

- **No pruning of candidate pairs.** Every possible pair within a document is currently considered, which grows quickly for long notes. Filtering pairs by distance or concept type could cut this down.
- **No explicit handling of long-distance relations.** The current focus is on pairs within the same document; relations that span across sentences or sections aren't specifically handled yet.
