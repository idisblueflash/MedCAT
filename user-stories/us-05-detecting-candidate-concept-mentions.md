# US 05 Detecting Candidate Concept Mentions in Text

As a *clinician analysing free-text notes*, I want to *find every span of text that could be a concept*, so that *the linker has candidates to disambiguate and nothing that matters is missed before the expensive step runs*.

This is the recogniser, and it is a dictionary matcher — no model, no weights, just lookups. Walking the non-skipped tokens left to right, `NER.__call__` (`medcat/ner/vocab_based_ner.py:24`) tries each token's normalised form and its lowercase form against two structures built in US 01: `name2cuis` (this is a complete name) and `snames` (this is a *prefix* of some name). A token that is a complete name is annotated immediately; a token that is merely a prefix is held open and the next token is appended — and the next — for as long as the growing string stays in `snames`. Every time the grown string is *also* a complete name, that span is annotated too. The moment the string stops being a prefix of anything, the walk breaks.

The consequence, and it is the whole design, is that this stage **over-produces on purpose**. It emits overlapping, nested candidates — "diabetes", "diabetes mellitus", and "diabetes mellitus type 2" can all be annotated from one walk — and each carries `_.link_candidates`, the full list of CUIs that name could mean. Nothing here decides: confidence is set to `-1` explicitly, a marker meaning "not computed". Resolution happens in US 06 (which CUI) and US 07 (which span wins).

## Acceptance Criteria

1. Given a token whose normalised or lowercase form is a complete name in `name2cuis`, and the token is not a stopword
   - when NER walks it
     - then a `Span` is created with `_.detected_name` set and `_.link_candidates` set to *every* CUI that name maps to
2. Given a token that is only a prefix (in `snames`, not in `name2cuis`)
   - when the next tokens are appended one at a time
     - then the span keeps growing while it remains in `snames`, and is emitted each time it also becomes a complete name — so longer matches are found without losing the shorter ones
3. Given a gap of more than `ner.max_skip_tokens` (default `2`, `medcat/config.py:434`) skipped tokens between two tokens
   - when NER walks across it
     - then the walk breaks — a name cannot be assembled across an arbitrarily long gap
4. Given a candidate name shorter than `ner.min_name_len` (default `3`, `medcat/config.py:432`)
   - when NER evaluates it
     - then it is not annotated at all
5. Given a name at least `min_name_len` but shorter than `ner.upper_case_limit_len` (default `4`, `medcat/config.py:439`)
   - when NER evaluates it
     - then it is annotated only if it is a single, fully-uppercase token — which lets `MI` through while suppressing stray short lowercase strings
6. Given `ner.check_upper_case_names` is on and the CDB recorded the name as uppercase-only
   - when NER matches
     - then the text tokens must also be uppercase, or the match is rejected
7. Given `ner.try_reverse_word_order` is on and the forward assembly fails
   - when NER retries
     - then the reversed two-part form is tried against `snames` before giving up

## Case handling (greedy prefix walk, deliberate over-production)

The matcher classifies each growing string into one of three states — complete name, prefix-only, neither — and dispatches: annotate, keep growing, break. It never chooses between overlapping matches and never scores anything; every ambiguity it finds it forwards. That is what makes the later stages tractable: by the time the context model runs (US 06), the candidate set is already closed.

## Later stages (deferred)

- **No fuzzy matching.** A name is matched or it is not; the only tolerance is whatever US 04's spell-checker bought upstream.
- **`try_reverse_word_order` is a two-term hack.** It handles `pain abdominal` → `abdominal pain`; it does not generalise to longer permutations.
- **Normalised vs. lowercase preference is unresolved.** Source `TODO`s ask whether the normalised or the lowercase hit should win when both match; currently the normalised one does, by list order.
