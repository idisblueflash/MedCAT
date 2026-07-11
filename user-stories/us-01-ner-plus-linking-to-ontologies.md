# US 01 Named Entity Recognition and Linking to Clinical Ontologies

As a *clinical NLP engineer*, I want to *extract concept mentions from free-text notes and link each to a stable ontology identifier*, so that *downstream analytics run on coded concepts (UMLS/SNOMED-CT CUIs) instead of raw strings*.

`CAT.get_entities(text)` runs the full spaCy-based pipeline (tokenization, candidate span detection, disambiguation) over a document and returns, for every detected entity, its concept unique identifier (CUI), matched text span, and pretty name. `get_entities_multi_texts` extends this to batches of documents in one call.

The risk is ambiguity: the same surface string can map to multiple CUIs depending on context (e.g. "cold" as a symptom vs. a temperature). The linker (`medcat/linking/context_based_linker.py`, `vector_context_model.py`) builds a context vector around each mention and compares it against learned per-CUI vectors, accepting a link only when similarity clears a configurable `similarity_threshold` (default `0.25`, `medcat/config.py`) — so a merely plausible surface match is never accepted as a confident link.

## Acceptance Criteria

1. Given a clinical document
   - when `get_entities(text)` runs the pipeline
     - then each detected entity is returned with its CUI, character offsets, and source name
2. Given a name that maps to multiple CUIs
   - when the linker scores the candidates against the surrounding context
     - then the CUI whose learned context vector best matches is chosen (only above `similarity_threshold`) — never simply the most frequent CUI
3. Given `addl_info` keys such as `cui2icd10` / `cui2snomed` / `cui2ontologies` are requested
   - when annotation runs
     - then each result additionally carries the requested cross-ontology references
4. Given `only_cui=True`
   - then the output is restricted to bare CUIs for lightweight downstream use
5. Given a batch of documents
   - when `get_entities_multi_texts` runs
     - then results are returned in the same order as the input documents

## Case handling (detect-then-link)

The pipeline first detects candidate spans, then links each. The span detector can be the built-in dictionary NER (`medcat/ner/vocab_based_ner.py`) or a transformer model (`medcat/ner/transformers_ner.py`). Disambiguation only engages for names shorter than `disamb_length_limit` (default `3` tokens), since longer names are rarely ambiguous; context vectors are sized per proximity band via `context_vector_sizes` (`{'xlong': 27, 'long': 18, 'medium': 9, 'short': 3}`).

## Later stages (deferred)

- **Threshold calibration.** `similarity_threshold` is a single global default; per-CUI or per-type thresholds would cut both missed links and false positives on skewed concepts.
- **Detector selection guidance.** The dictionary vs. transformer NER trade-off (speed vs. recall) is left to the caller; a documented decision guide would help new users pick.
