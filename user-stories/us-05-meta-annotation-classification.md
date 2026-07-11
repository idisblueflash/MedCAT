# US 05 Meta-Annotation Classification with MetaCAT

As a *clinical NLP engineer*, I want to *classify contextual attributes (negation, experiencer, temporality) on already-linked spans*, so that *downstream consumers can filter out negated or non-patient mentions without retraining the linker*.

`MetaCAT` (`medcat/meta_cat.py`) trains and runs secondary classifiers (BiLSTM or transformer, optionally fine-tuned efficiently via LoRA through `peft`) over each detected span to answer one contextual question — for example, whether a finding is affirmed or negated. Multiple `MetaCAT` instances can attach to one `CAT` pipeline via `meta_cats=[...]`, each answering a different question over the same spans.

Meta-annotation is deliberately decoupled from the base NER+L decision: a concept can be correctly linked to "chest pain" and still be classified as negated or reported by a family member. Keeping the two separate means consumers filter on the classification without touching or retraining the linking model.

## Acceptance Criteria

1. Given one or more `MetaCAT` models attached to a pipeline
   - when a document is annotated
     - then each model produces an independent classification per entity span
2. Given a new clinical use case with different labels
   - when a `MetaCAT` is configured
     - then its category values (e.g. Affirmed / Other) are set by config rather than hardcoded
3. Given a MedCATtrainer JSON export
   - when `prepare_from_json` runs
     - then training data is prepared in the same format used by supervised training (US 04)
4. Given the publicly distributed `mc_status` model
   - when it runs over an annotation
     - then it classifies whether the annotation is Affirmed (Positive) or Other (Negated/Hypothetical)

## Case handling (span-level classifiers)

Each attached model is an independent classifier keyed to the same spans, so questions compose without interfering. Data preparation lives in `medcat/utils/meta_cat/data_utils.py`; training/evaluation loops (`train_model`, `eval_model`, `set_all_seeds`) in `medcat/utils/meta_cat/ml_utils.py`; tokenization in `medcat/tokenizers/meta_cat_tokenizers.py`; behaviour configured through `medcat/config_meta_cat.py`.

## Later stages (deferred)

- **Shared encoder.** Each MetaCAT carries its own model; a shared span encoder across tasks would cut memory and inference cost when many are attached.
- **Label-set governance.** Category values are free-form per model; a shared vocabulary of standard attributes would improve cross-model comparability.
