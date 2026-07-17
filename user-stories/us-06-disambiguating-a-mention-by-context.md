# US 06 Disambiguating an Ambiguous Mention Using Its Context

As a *clinician analysing free-text notes*, I want to *have "cold" resolved to the infection or the temperature feeling, depending on the words around it*, so that *the annotation actually means something, instead of an arbitrary pick from a list of same-spelled meanings*.

US 05 hands over text spans, each carrying a list of possible concept codes (CUIs). This step is where MedCAT picks one — or decides none of them fit.

`ContextModel` (`medcat/linking/vector_context_model.py:15`) builds a vector (a list of numbers) describing the words around the mention. It looks at four window sizes at once — `short` (3 tokens), `medium` (9), `long` (18), `xlong` (27) — and for each one, it collects the nearby words (skipping stopwords, digits, and punctuation), looks up each word's embedding in the `Vocab` (US 03), and averages them. Closer words count more than farther ones (this is called "distance-weighting"). This average is then compared, using something called cosine similarity (`_similarity`, `:112`), against a vector learned separately for each candidate concept (see US 10 and US 11). The four window sizes are then combined using weights from `linking.context_vector_weights` (`medcat/config.py:540` — the `long` and `medium` windows count the most, 0.4 each). Whichever candidate scores highest wins.

Here's the catch: a *high* score is not the same thing as a *trustworthy* score. If a candidate concept hasn't been seen enough times during training — fewer than `linking.train_count_threshold` (`medcat/config.py:553`) — its similarity score is forced to `-1`. That's not zero, and it's not "no answer": it means this candidate can never win, but the system doesn't say why. On top of that, two extra "thumbs on the scale" are applied before picking the winner:

- `prefer_primary_name` (weight `0.35`, `:568`) gives a boost to a candidate whose matched name is its main/preferred name.
- `prefer_frequent_concepts` (weight `0.35`, `:570`) gives a boost based on how often that concept was seen in training.

Both boosts are capped at `0.99`. In short: the winner isn't simply "the best match for this context" — it's "the best match for this context, adjusted for popularity."

## Acceptance Criteria

1. Given a mention with more than one possible CUI
   - when the linker runs (outside of training mode)
     - then a decision is always forced: MedCAT scores every candidate and picks the highest
2. Given a mention with only one possible CUI, but that name is flagged `N` (not preferred) or `PD` (needs a decision)
   - when the linker runs
     - then a decision is still forced — having just one candidate doesn't skip the check if the CDB flagged that name as uncertain
3. Given a detected name shorter than `linking.disamb_length_limit` (3 letters by default — `medcat/config.py:549`)
   - when the linker runs
     - then a decision is forced no matter how many candidates there are — short names are never trusted blindly
4. Given a single candidate flagged `P` (preferred) or `A` (automatic), with a name at or above the length limit
   - when the linker runs
     - then it's linked directly, with similarity automatically set to `1` and no vector computed (unless the setting `always_calculate_similarity` says otherwise — `:556`)
5. Given the winning CUI's similarity score is below `linking.similarity_threshold` (0.25 by default — `:563`)
   - when the threshold check runs
     - then the entity is dropped entirely — it is not kept with low confidence, it's simply not annotated
6. Given `linking.similarity_threshold_type` is set to `dynamic` (`:562`)
   - when the threshold check runs
     - then the bar becomes `cui2average_confidence[cui] * similarity_threshold` — a threshold learned separately for each concept, so concepts that are naturally harder to match aren't held to the same fixed bar as easy ones
7. Given the winning CUI is excluded by an active filter (US 08)
   - when the filter is applied
     - then it is dropped, even though it scored the highest
8. Given a candidate CUI has fewer training examples than `train_count_threshold`
   - when its similarity is computed
     - then the score is `-1`, and it can never win

## Case handling (first decide if a decision is needed, then score)

The linker first checks whether a decision is even necessary — is the name too short? are there multiple candidates? is it flagged `N` or `PD`? Only if the answer is yes does it bother computing vectors. Anything that gets past that stage must then clear both a similarity threshold and a filter — three separate checkpoints, and failing any one of them silently drops the entity. If an entity you expected seems to have "vanished," it could have failed at any of these three points, and the output (US 09) won't tell you which one.

## Later stages (deferred)

- **`filter_before_disamb`.** When this is turned on, filtering happens *before* picking the winner instead of after — which can change the actual result, not just the speed (see US 08).
- **The popularity boosts are unproven constants.** `prefer_primary_name` and `prefer_frequent_concepts` both default to `0.35` with no documented reasoning behind that number, and both directly affect which candidate wins.
- **Cold start problem.** A concept with no training examples has no context vector and can't be matched by context at all — the only way to link it is the direct-link shortcut (see AC4), which happens to be the one path that skips this whole check.
