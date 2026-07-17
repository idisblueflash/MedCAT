# US 05 Detecting Candidate Concept Mentions in Text

As a *clinician analysing free-text notes*, I want to *find every stretch of text that could be a medical concept*, so that *the linker has candidates to choose between, and nothing important is missed before the more expensive step runs*.

This step is the recogniser, and it is a simple dictionary matcher — no machine-learning model, no learned weights, just lookups in a table. It reads the text left to right, skipping any token already marked `to_skip` (US 04). For each remaining token, `NER.__call__` (`medcat/ner/vocab_based_ner.py:24`) checks its normalised form and its lowercase form against two lookup tables built back in US 01:

- `name2cuis` — "this exact string is a complete concept name."
- `snames` — "this string is the *beginning* of some concept name, but maybe not the whole thing."

If a token is a complete name, it's marked right away as a match. If a token is only the beginning of a longer name, MedCAT holds it open and keeps adding the next token, then the next, for as long as the growing string is still the beginning of *something* in `snames`. Every time that growing string also happens to be a complete name, it gets marked as a match too. The moment the string stops being the start of anything, MedCAT gives up and moves on.

Here's the key design decision behind all of this: this step deliberately finds **too many** matches, not too few. It's fine, even expected, for matches to overlap and nest inside each other — from one pass over the text, "diabetes", "diabetes mellitus", and "diabetes mellitus type 2" can all be found as candidates. Each match is tagged with `_.link_candidates`, the complete list of concept codes (CUIs) that name could possibly mean. Nothing here decides which meaning is correct — the confidence score is deliberately set to `-1`, meaning "not decided yet." Deciding which CUI is right happens in US 06, and deciding which overlapping span wins happens in US 07.

## Acceptance Criteria

1. Given a token whose cleaned-up or lowercase form is a complete name in `name2cuis`, and it isn't a stopword
   - when the recogniser walks through it
     - then a match (`Span`) is created, storing the matched name and *every* CUI it could mean
2. Given a token that's only the start of a longer name (in `snames` but not yet a full name in `name2cuis`)
   - when the following tokens are added one at a time
     - then the match keeps growing as long as it's still the start of something, and gets recorded every time it also becomes a full name — so both the shorter and the longer matches are kept
3. Given a gap of more than `ner.max_skip_tokens` (2, by default — `medcat/config.py:434`) skipped tokens between two tokens
   - when the recogniser tries to walk across that gap
     - then it stops — a name cannot be built by jumping across an arbitrarily wide gap
4. Given a candidate name shorter than `ner.min_name_len` (3 letters by default — `medcat/config.py:432`)
   - when the recogniser checks it
     - then it isn't recorded as a match at all — it's too short to be reliable
5. Given a name that is at least `min_name_len` but shorter than `ner.upper_case_limit_len` (4 letters by default — `medcat/config.py:439`)
   - when the recogniser checks it
     - then it's only accepted if it's a single word written fully in capital letters — this lets abbreviations like `MI` through while blocking random short lowercase strings
6. Given `ner.check_upper_case_names` is turned on, and the CDB recorded that name as capital-letters-only
   - when the recogniser tries to match it
     - then the text must also be in capital letters, or the match is rejected
7. Given `ner.try_reverse_word_order` is turned on, and building the name forwards fails
   - when the recogniser retries
     - then it tries the two words in reversed order against `snames` before giving up entirely

## Case handling (a growing string is always in one of three states)

At every step, the growing string is either a complete name, only the start of a name, or neither. The recogniser reacts accordingly: record a match, keep growing, or stop. It never picks a winner among overlapping matches, and it never scores anything — every bit of ambiguity it finds gets passed forward. This is exactly what makes the later steps manageable: by the time the context model runs (US 06), the full list of candidates is already fixed.

## Later stages (deferred)

- **No fuzzy matching here.** A name either matches exactly or it doesn't; the only tolerance for typos comes from the spell-checker upstream in US 04.
- **`try_reverse_word_order` only handles two-word swaps.** It fixes cases like `pain abdominal` → `abdominal pain`, but doesn't extend to longer reorderings.
- **Normalised vs. lowercase priority is still an open question.** Comments in the source code (`TODO`s) ask which one should win when both match the same text; right now the normalised form wins, simply because of list order.
