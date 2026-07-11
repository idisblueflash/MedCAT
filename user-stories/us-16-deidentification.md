# US 16 De-Identification of Clinical Text

As a *data engineer*, I want to *detect and redact PII/PHI in clinical free text*, so that *notes can be shared or stored more broadly without exposing patient identifiers*.

`DeIdModel` (`medcat/utils/ner/deid.py`) wraps a regular `CAT` pipeline configured with a PII-focused NER component, exposing a simplified API for the two cases that matter: creating a new de-identification model from an NER component (`DeIdModel.create(ner)`) and loading an existing one (`DeIdModel.load_model_pack(path)`). `deid.deid_text(text)` returns anonymised text directly, while `deid(text)` returns the full spaCy `Doc` for callers that need structured spans.

The wrapper exists to collapse what would otherwise be manual pipeline assembly (`CAT(cdb=ner.cdb, addl_ner=ner)` plus a separate `deid_text(cat, text)` helper) into one coherent object, while still exposing the underlying `config` and `cdb` for inspection. This keeps de-identification from requiring users to learn CAT's general-purpose construction API just to redact a document.

## Acceptance Criteria

1. Given a PII-focused NER component
   - when `DeIdModel.create(ner)` is called
     - then a working de-identification model is built from it
2. Given a previously packaged de-identification model pack
   - when `DeIdModel.load_model_pack(path)` is called
     - then the model loads ready for use
3. Given a clinical document
   - when `deid_text(text)` runs
     - then anonymised text is returned, suitable for direct storage or sharing
4. Given a caller needs structured output
   - when `deid(text)` runs
     - then a spaCy `Doc` with entity spans and labels is returned for downstream processing

## Case handling (model detection + regex redaction)

Detection builds on the transformer-based NER component (`medcat/ner/transformers_ner.py`); the module also imports `re` to support regex-based redaction patterns alongside model-based detection, so structured identifiers can be caught even where the model is uncertain. Redaction has two output modes — replaced text vs. structured `Doc` — selected by which method the caller invokes.

## Later stages (deferred)

- **Recall auditing.** There is no built-in leakage/recall report; a held-out PHI evaluation harness would quantify residual risk before release.
- **Configurable redaction tokens.** Replacement formatting is fixed by the helper; per-entity-type placeholders (e.g. `[NAME]`, `[DATE]`) would aid readability of redacted output.
