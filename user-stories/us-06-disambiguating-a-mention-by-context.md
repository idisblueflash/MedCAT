# US 06 Disambiguating an Ambiguous Mention Using Its Context

As a *clinician analysing free-text notes*, I want to *have "cold" resolved to the infection or the temperature sensation depending on the surrounding words*, so that *the annotation means something rather than being an arbitrary pick from a list of homonyms*.

US 05 hands over spans carrying a list of candidate CUIs; this is the step that picks one — or rejects all of them. `ContextModel` (`medcat/linking/vector_context_model.py:15`) builds a vector for the mention's surroundings: for each of four context widths (`short` 3 tokens, `medium` 9, `long` 18, `xlong` 27) it collects the non-skipped, non-stopword, non-digit, non-punctuation tokens to the left and right, looks up each one's embedding in the `Vocab` (US 03), and averages them — with left/right tokens *distance-weighted* so nearer words count for more. That is compared by cosine similarity (`_similarity`, `:112`) against each candidate CUI's learned context vector (US 10, US 11), and the four widths are recombined by `linking.context_vector_weights` (`medcat/config.py:540`; long and medium dominate at `0.4` each). Highest score wins.

The risk is that a *high* score and a *trustworthy* score are not the same thing. `_similarity` returns `-1` — not zero, not `None` — for any CUI whose `cui2count_train` is below `linking.train_count_threshold` (`medcat/config.py:553`), so an untrained concept can never win but also never explains why it lost. And two thumbs are put on the scale before the argmax: `prefer_primary_name` (`0.35`, `:568`) inflates a candidate whose name is its primary form, and `prefer_frequent_concepts` (`0.35`, `:570`) inflates candidates by the log of their training count. Both are capped at `0.99`, and both mean the winner is not simply the best contextual match — it is the best contextual match after a popularity adjustment.

## Acceptance Criteria

1. Given a mention with more than one candidate CUI
   - when the linker runs outside training mode
     - then disambiguation is forced, similarity is computed per candidate, and the argmax wins
2. Given a mention with exactly one candidate CUI whose `(name, cui)` status is `N` or `PD`
   - when the linker runs
     - then disambiguation is still forced — a single candidate is not a free pass if the CDB flagged that name as needing a decision
3. Given a detected name shorter than `linking.disamb_length_limit` (default `3`, `medcat/config.py:549`)
   - when the linker runs
     - then disambiguation is forced regardless of candidate count — short names are never trusted on their own
4. Given a single candidate with status `P` or `A` and a name at or above the length limit
   - when the linker runs
     - then it is linked directly with similarity `1` and no vector is computed (unless `always_calculate_similarity` is set, `:556`)
5. Given a winning CUI whose similarity is below `linking.similarity_threshold` (default `0.25`, `:563`)
   - when the threshold is applied
     - then the entity is dropped — it is not annotated with low confidence, it is not annotated at all
6. Given `linking.similarity_threshold_type` is `dynamic` (`:562`)
   - when the threshold is applied
     - then the bar is `cui2average_confidence[cui] * similarity_threshold` — a per-concept threshold learned during training, so concepts that are inherently hard to match are not held to the same absolute bar
7. Given a winning CUI excluded by the active filters (US 08)
   - when the filter is applied
     - then it is dropped, even if it scored highest
8. Given a candidate CUI with fewer than `train_count_threshold` training examples
   - when similarity is computed
     - then its similarity is `-1` and it cannot win

## Case handling (decide-whether-to-decide, then score)

The linker first classifies whether a decision is even needed — short name? multiple candidates? flagged `N`/`PD`? — and only pays for vectorisation when the answer is yes. Everything that survives scoring must then clear a threshold and a filter: three independent gates, any of which drops the entity silently. An entity that "disappeared" could have failed at any one of them, and the output format (US 09) does not say which.

## Later stages (deferred)

- **`filter_before_disamb`.** When set, candidates are filtered *before* the argmax rather than after — which changes results, not just performance (US 08).
- **The preference bonuses are untuned constants.** `prefer_primary_name` and `prefer_frequent_concepts` both default to `0.35` with no stated derivation, and both directly move the argmax.
- **Cold-start.** A concept with no training has no vector and cannot be linked by context; it can only be reached via the direct-link path (AC4) — exactly the path that skips the check.
