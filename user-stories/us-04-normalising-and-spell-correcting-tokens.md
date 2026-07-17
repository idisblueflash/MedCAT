# US 04 Normalising and Spell-Correcting Tokens Before Matching

As a *clinician analysing free-text notes*, I want to *have misspellings and word-endings fixed before concept matching runs*, so that *"diabets mellitus" and "enlarged livers" still find the right concepts, instead of being missed by an exact dictionary lookup*.

The CDB stores concept names in a cleaned-up form: lowercase, and reduced to their base word (this is called a "lemma" — for example "livers" becomes "liver"). So before MedCAT can match anything in incoming text, it first has to clean the text the same way. Two steps do this, one after another:

1. **Tagging.** `tag_skip_and_punct` (`medcat/preprocessing/taggers.py:7`) marks some tokens as `to_skip` — meaning "ignore this one." This includes punctuation that isn't in the `preprocessing.keep_punct` list, filler words in `preprocessing.words_to_skip` (by default just `{'nos'}`), and optionally stopwords (common words like "the" or "and").
2. **Normalising.** `TokenNormalizer` (`medcat/utils/normalizers.py:162`) sets `token._.norm` (the cleaned-up form) to the lowercase lemma of the word. There are two exceptions: if the word is shorter than `preprocessing.min_len_normalize` (5 letters by default), or if its grammar tag is in `preprocessing.do_not_normalize` (things like comparatives or past-tense verbs), MedCAT keeps the plain lowercase form instead of the lemma, because shortening it further could lose meaning.

If the setting `general.spell_check` is turned on, there's a third step: a spelling checker (`BasicSpellChecker`, `medcat/utils/normalizers.py:10`) that works like a classic "Did you mean...?" tool, based on how many single-letter edits separate two words.

Here is the part to be careful about: spell-checking only runs on words the CDB has **never seen**. `BasicSpellChecker.__contains__` only returns `True` for words that are literally in the CDB's own vocabulary. A word that exists in everyday English but isn't a CDB name will be treated as *possibly misspelled*, even if it's spelled correctly. In other words, a normal English word can get "corrected" into a medical term just because the medical term happens to be in the CDB and the everyday word isn't. The safety checks against this are simple: a minimum word length (`general.spell_check_len_limit`, 7 letters by default, `medcat/config.py:376`), and refusing to touch anything with a digit in it.

## Acceptance Criteria

1. Given a token that is at least `min_len_normalize` letters long, with a grammar tag that can be normalised
   - when the normalizer runs
     - then `token._.norm` becomes its lowercase base form, matching how the CDB stored it
2. Given a token shorter than `min_len_normalize`, or tagged as a past-tense verb, gerund, comparative, or similar
   - when the normalizer runs
     - then it is kept as its plain lowercase form — shortening it further would lose the distinction that tag was marking
3. Given spell-check is on, and a token is long enough, not punctuation, has no digits, and isn't in the CDB vocabulary
   - when spelling candidates are generated (one edit away, or two if `general.spell_check_deep` is on)
     - then the most likely known word replaces it, and that replacement is then normalised too
4. Given a token that is in the CDB vocabulary
   - when normalisation runs
     - then it is never "corrected," even if it happens to be misspelled
5. Given a token is punctuation and isn't in `keep_punct`
   - when tagging runs
     - then it is marked `is_punct` and `to_skip`, so both the recogniser (US 05) and the context window (US 06) skip right over it

## Case handling (skip, normalise, or normalise-then-correct)

Every token is sorted into exactly one path: skipped, normalised, or normalised and then spell-corrected. There's no going back — the original spelling is still stored on the token (as `source_value` in the final output, see US 09), but the matching itself only ever looks at the cleaned-up form. This means a wrong spelling-correction is invisible in the output unless you specifically compare `detected_name` against `source_value`. Tests for this live in `tests/utils/test_normalizers.py`.

## Later stages (deferred)

- **"Confidence" is really just word frequency.** The number used to rank spelling candidates, `P(word)`, is a stand-in based on rank (`-1/count`), not a real probability — and there's no cutoff below which MedCAT refuses to correct a word.
- **No log of corrections.** Nothing records which words were rewritten by spell-check, which makes it hard to trace a wrong annotation back to a spelling "fix" that shouldn't have happened.
