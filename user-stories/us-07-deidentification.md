# US 07 De-Identification of Clinical Text

This specification describes MedCAT's specialised workflow for detecting and redacting personally identifiable information (PII/PHI) in clinical free text before it is shared or stored more broadly.

## Core Purpose

`DeIdModel` (`medcat/utils/ner/deid.py`) wraps a regular `CAT` pipeline configured with a PII-focused NER component, exposing a simplified API for the two use cases that matter here: creating a new de-identification model from an NER component (`DeIdModel.create(ner)`) and loading an existing one for use (`DeIdModel.load_model_pack(path)`). `deid.deid_text(text)` returns anonymised text directly, while `deid(text)` returns the full spaCy `Doc` for callers that need structured entity spans rather than a redacted string.

## Key Design Consideration

The wrapper exists specifically to collapse what would otherwise be manual pipeline assembly (`CAT(cdb=ner.cdb, addl_ner=ner)` followed by a separate `deid_text(cat, text)` helper call) into one coherent object, while still exposing the underlying `config` and `cdb` directly for cases where a caller needs to inspect or adjust the wrapped model. This keeps de-identification from requiring users to understand CAT's general-purpose construction API just to redact a document.

## Acceptance Criteria Summary

The specification requires:
- `DeIdModel.create` builds a working de-identification model from a supplied NER component
- `DeIdModel.load_model_pack` loads a previously packaged de-identification model pack
- `deid_text` returns anonymised text suitable for direct storage or sharing
- `deid(text)` (structured mode) returns a spaCy `Doc` with entity spans and labels for downstream structured processing

## Implementation Notes

The detection layer builds on the transformer-based NER component (`medcat/ner/transformers_ner.py`), and the module additionally imports `re` to support regex-based redaction patterns alongside model-based detection.
