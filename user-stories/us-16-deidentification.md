# US 16 De-Identification of Clinical Text

As a *data engineer*, I want to *detect and hide personal patient information in clinical free text*, so that *notes can be shared or stored more widely without exposing who the patient is*.

("PII" means personally identifiable information — like a name or ID number. "PHI" means protected health information — the healthcare version of the same idea. "De-identification" or "redaction" means finding and removing or masking this information.)

`DeIdModel` (`medcat/utils/ner/deid.py`) wraps a regular `CAT` pipeline (US 05–09), set up with a component specifically trained to detect personal information, and gives you a simple way to use it for the two things you'll actually need:

- Build a new de-identification model from a detection component: `DeIdModel.create(ner)`
- Load an existing, already-built one: `DeIdModel.load_model_pack(path)`

Once you have a model, `deid.deid_text(text)` gives you back the anonymised text directly. If you need more detail — the exact spans that were found and labelled — `deid(text)` gives you the full spaCy `Doc` object instead.

The point of this wrapper is to save you from manually assembling a pipeline yourself (which would otherwise mean writing something like `CAT(cdb=ner.cdb, addl_ner=ner)` plus a separate helper function). Instead, you get one simple object that still lets you inspect the underlying `config` and `cdb` if you need to. This means you don't have to learn MedCAT's general pipeline-building API just to redact a document.

## Acceptance Criteria

1. Given a detection component trained to find personal information
   - when `DeIdModel.create(ner)` is called
     - then a working de-identification model is built from it
2. Given an already-packaged de-identification model
   - when `DeIdModel.load_model_pack(path)` is called
     - then the model loads and is ready to use
3. Given a clinical document
   - when `deid_text(text)` runs
     - then anonymised text comes back, ready to store or share directly
4. Given a caller needs the detailed, structured output instead of just plain text
   - when `deid(text)` runs
     - then a spaCy `Doc` with entity spans and labels is returned for further processing

## Case handling (model detection plus pattern-based redaction)

Detection is built on the transformer-based recogniser from US 15 (`medcat/ner/transformers_ner.py`). The module also uses regular expressions (`re`) for pattern-based redaction, so structured identifiers (like ID numbers with a known format) can still be caught even in cases where the model itself is unsure. There are two output styles — plain redacted text, or a structured `Doc` — and you choose between them just by which method you call.

## Later stages (deferred)

- **No built-in leakage check.** There's currently no automatic report measuring how much personal information might slip through undetected; a held-out test specifically for this would help quantify the remaining risk before using this in production.
- **Redaction placeholders aren't customizable.** The text used to replace hidden information is currently fixed. Type-specific placeholders (like `[NAME]` or `[DATE]`) would make redacted text easier to read.
