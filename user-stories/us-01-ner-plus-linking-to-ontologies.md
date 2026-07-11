# US 01 Named Entity Recognition and Linking to Clinical Ontologies

This specification describes MedCAT's core capability: extracting concept mentions from free-text clinical documents and linking each mention to a stable identifier in a biomedical ontology such as UMLS or SNOMED-CT.

## Core Purpose

`CAT.get_entities(text)` runs the full spaCy-based pipeline (tokenization, candidate span detection, disambiguation) over a document and returns a structured result containing the concept unique identifier (CUI), matched text span, and pretty name for every detected entity. `get_entities_multi_texts` extends this to batches of documents in one call.

## Key Design Consideration

Names are frequently ambiguous — the same surface string can map to multiple CUIs depending on context (e.g. "cold" as a symptom vs. a temperature description). The linker (`medcat/linking/context_based_linker.py`, `medcat/linking/vector_context_model.py`) builds a context vector around each mention and compares it against learned per-CUI vectors, only accepting a link when similarity clears a configurable `similarity_threshold` (default `0.25`, `medcat/config.py`). This prevents a merely plausible surface match from being accepted as a confident link.

## Acceptance Criteria Summary

The specification requires:
- Calling `get_entities` on a text returns each entity's CUI, character offsets, and source name
- Ambiguous names are disambiguated using surrounding context rather than the first/most frequent CUI
- `addl_info` (e.g. `cui2icd10`, `cui2snomed`, `cui2ontologies`) optionally attaches cross-ontology references to each result
- `only_cui=True` restricts output to bare CUIs for lightweight downstream use
- Batch annotation via `get_entities_multi_texts` produces results in the same order as the input documents

## Implementation Notes

Context vectors are sized per proximity band via `context_vector_sizes` (`{'xlong': 27, 'long': 18, 'medium': 9, 'short': 3}`), and disambiguation only engages for names shorter than `disamb_length_limit` (default `3` tokens) since longer names are rarely ambiguous. The underlying span detector can be the built-in dictionary-based NER (`medcat/ner/vocab_based_ner.py`) or a transformer-based model (`medcat/ner/transformers_ner.py`).
