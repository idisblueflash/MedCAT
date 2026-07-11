# US 04 Normalising and Spell-Correcting Tokens Before Matching

As a *clinician analysing free-text notes*, I want to *have misspellings and inflections resolved before concept matching runs*, so that *"diabets mellitus" and "enlarged livers" still hit the concepts they mean instead of being missed by an exact dictionary lookup*.

The CDB stores names in a normalised form (lemmatised, lowercased — see US 01), so incoming text must be pushed into the same space or nothing matches. Two components do this in order. The tagger `tag_skip_and_punct` (`medcat/preprocessing/taggers.py:7`) marks tokens `to_skip` — punctuation not in `preprocessing.keep_punct`, strings in `preprocessing.words_to_skip` (default `{'nos'}`), and optionally stopwords. Then `TokenNormalizer` (`medcat/utils/normalizers.py:162`) sets `token._.norm` to the lowercased lemma — unless the token is shorter than `preprocessing.min_len_normalize` (default `5`) or carries a POS tag in `preprocessing.do_not_normalize` (comparatives, past participles), in which case the raw lowercase form is kept. Finally, if `general.spell_check` is on, a Norvig-style edit-distance checker (`BasicSpellChecker`, `medcat/utils/normalizers.py:10`) rewrites the token.

The risk is that spell-checking is applied *only to words the CDB has never seen*. `BasicSpellChecker.__contains__` returns `True` only for words in the **CDB vocabulary**; a word present in the general data vocab but not the CDB returns `False` deliberately, so it becomes a correction candidate. A legitimate English word can therefore be "corrected" into a medical term simply because the medical term is in the CDB and the English word is not. The guard rails are crude: a minimum length (`general.spell_check_len_limit`, default `7`, `medcat/config.py:376`) and a refusal to touch anything containing a digit.

## Acceptance Criteria

1. Given a token of length ≥ `min_len_normalize` with a normalisable POS tag
   - when the normalizer runs
     - then `token._.norm` is its lowercased lemma, matching the form the CDB stored
2. Given a token shorter than `min_len_normalize`, or tagged `VBD`/`VBG`/`VBN`/`VBP`/`JJS`/`JJR`
   - when the normalizer runs
     - then it is left as lowercase surface form — lemmatising it would destroy the distinction the tag encodes
3. Given spell-check is on and a token is long enough, non-punctuation, digit-free, and not in the CDB vocabulary
   - when candidates are generated (one edit away, or two if `general.spell_check_deep`)
     - then the highest-probability known candidate replaces it, and the replacement is itself re-lemmatised
4. Given a token that is in the CDB vocabulary
   - when normalisation runs
     - then it is never corrected, regardless of whether it is a real word
5. Given a token matching `punct_checker` and not in `keep_punct`
   - when tagging runs
     - then it is marked `is_punct` and `to_skip`, and both the recogniser (US 05) and the context window (US 06) step over it

## Case handling (skip → normalise → maybe-correct)

Each token is classified once and dispatched: skip it, normalise it, or normalise then correct it. There is no round-trip — the original surface form survives on the token (`source_value` in the output, US 09), but matching sees only `._.norm` and `.lower_`, so a wrongly-fired correction is invisible in the final annotation unless `detected_name` is inspected against `source_value`. Coverage lives in `tests/utils/test_normalizers.py`.

## Later stages (deferred)

- **Correction confidence is a frequency proxy.** `P(word)` is an inverse-rank stand-in (`-1/count`), not a probability; there is no threshold below which a correction is refused.
- **No correction logging.** Nothing records which tokens were rewritten, so a spell-check-induced false positive is very hard to trace back.
