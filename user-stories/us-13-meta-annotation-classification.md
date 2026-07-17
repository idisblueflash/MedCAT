# US 13 Meta-Annotation Classification with MetaCAT

As a *clinical NLP engineer*, I want to *classify extra context about an already-linked concept — like whether it's negated, who experienced it, or when it happened*, so that *downstream users can filter out negated or non-patient mentions, without having to retrain the linker itself*.

`MetaCAT` (`medcat/meta_cat.py`) trains and runs extra classifiers (using either a BiLSTM or a transformer model, which can be efficiently fine-tuned with a technique called LoRA through the `peft` library) on top of every already-detected span. Each classifier answers one specific yes/no-style question — for example: is this finding affirmed, or is it negated? You can attach several `MetaCAT` instances to one pipeline at once, using `meta_cats=[...]`, and each one can answer a different question about the same spans.

This "meta-annotation" step is kept deliberately separate from the main linking decision. A concept can be correctly linked to "chest pain," and still be classified separately as negated, or as something reported by a family member rather than the patient. Keeping these two decisions apart means you can filter based on the classification, without ever touching or retraining the main linking model.

## Acceptance Criteria

1. Given one or more `MetaCAT` models attached to a pipeline
   - when a document is annotated
     - then each model produces its own, independent classification for every entity span
2. Given a new clinical use case that needs different labels
   - when a `MetaCAT` model is configured
     - then its category labels (for example, "Affirmed" / "Other") are set through configuration, not hardcoded into the code
3. Given a MedCATtrainer JSON export
   - when `prepare_from_json` runs
     - then training data is prepared in the same format used for supervised training (US 11)
4. Given the publicly available `mc_status` model
   - when it runs on an annotation
     - then it labels the annotation as either Affirmed (Positive) or Other (Negated/Hypothetical)

## Case handling (each classifier looks at the same spans independently)

Each attached model works as its own independent classifier over the same set of spans, so different questions don't interfere with each other. Data preparation lives in `medcat/utils/meta_cat/data_utils.py`; training and evaluation logic (`train_model`, `eval_model`, `set_all_seeds`) lives in `medcat/utils/meta_cat/ml_utils.py`; tokenization lives in `medcat/tokenizers/meta_cat_tokenizers.py`; and settings are controlled through `medcat/config_meta_cat.py`.

## Later stages (deferred)

- **A shared encoder.** Right now every MetaCAT model carries its own full model. Sharing one encoder across several attached MetaCAT tasks would save memory and speed things up.
- **No shared naming rules for labels.** Category labels are currently free-form and chosen per model. A shared, standard vocabulary of attribute names would make results easier to compare across different models.
