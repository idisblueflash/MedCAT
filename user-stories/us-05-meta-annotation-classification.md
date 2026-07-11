# US 05 Meta-Annotation Classification with MetaCAT

This specification describes how MedCAT attaches contextual attributes — such as negation, experiencer, and temporality — to an already-linked concept mention, without altering the linking decision itself.

## Core Purpose

`MetaCAT` (`medcat/meta_cat.py`) trains and runs secondary classifiers (BiLSTM or transformer models, optionally fine-tuned efficiently via LoRA through `peft`) over each detected span to answer a specific contextual question, for example whether a finding is affirmed or negated. Multiple `MetaCAT` instances can be attached to one `CAT` pipeline via `meta_cats=[...]`, each answering a different question over the same spans.

## Key Design Consideration

Meta-annotation is deliberately decoupled from the base NER+L decision: a concept can be correctly linked to "chest pain" and still be classified as negated or reported by a family member rather than the patient, and downstream consumers can filter on that classification without needing to touch or retrain the linking model itself.

## Acceptance Criteria Summary

The specification requires:
- Each attached `MetaCAT` model produces an independent classification per entity span
- A model's category values (e.g. Affirmed / Other) are configurable rather than hardcoded to one clinical use case
- Training accepts a MedCATtrainer JSON export via `prepare_from_json`, mirroring the supervised-training data format used elsewhere in the pipeline
- The publicly distributed `mc_status` model demonstrates the pattern: detecting whether an annotation is Affirmed (Positive) or Other (Negated/Hypothetical)

## Implementation Notes

Data preparation lives in `medcat/utils/meta_cat/data_utils.py`, and training/evaluation loops in `medcat/utils/meta_cat/ml_utils.py` (`train_model`, `eval_model`, `set_all_seeds`). Tokenization is handled by `medcat/tokenizers/meta_cat_tokenizers.py`, with behaviour configured through `medcat/config_meta_cat.py`.
