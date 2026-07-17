# US 19 Measuring Performance Against a Gold Standard

As a *model builder deciding whether to deploy*, I want to *know the precision, recall, and F1 score for each concept, along with worked examples of the model's mistakes*, so that *I can judge whether the model is good enough, and see exactly which concepts it struggles with — because one overall F1 score hides all the details that actually matter*.

(A "gold standard" is a set of documents where the correct annotations are already known, usually because a human checked them. Precision, recall, and F1 are standard ways of measuring how good predictions are: precision asks "of what it found, how much was right?"; recall asks "of what was actually there, how much did it find?"; F1 combines both into one number.)

`get_stats(cat, data)` (`medcat/stats/stats.py:272`) replays a MedCATtrainer export: it runs the model on each document, compares the result to the human annotations, and keeps a running tally of true positives, false positives, and false negatives **for each individual concept**. From that, it works out precision, recall, and F1 per concept, plus `cui_counts`, plus the most useful part: `examples` — a dictionary of the actual sentences where the model got a false positive or false negative for each concept. A recall score of 0.6 on its own doesn't tell you what to fix; twenty example sentences of missed mentions for that concept will show you it's missing a specific abbreviation.

The tricky part is deciding what even counts as "a match," and there are four separate settings that each change the answer:

- `use_overlaps` (`:24`) — decides whether a span that overlaps the gold answer, but isn't identical to it, counts as correct.
- `use_cui_doc_limit` (`:25`) — restricts a concept's score to only the documents where that concept was actually annotated in the gold data. This matters a lot if your annotation guidelines changed partway through the project — otherwise, every document annotated before a concept was added counts as a false positive.
- `use_groups` — reports scores by concept *group* instead of individual concept, which makes the numbers look better because mix-ups within the same group are no longer counted as errors.
- `use_filters` — applies the project's own concept filter (US 08), so concepts outside the project's scope aren't scored at all.

None of these four settings are recorded together with the result. This means two F1 scores from this function are only comparable if you already know all four settings were the same both times.

## Acceptance Criteria

1. Given a model and a gold-standard export
   - when `get_stats` runs
     - then per-concept `tp`, `fp`, `fn`, `precision`, `recall`, `f1`, and `cui_counts` are returned, along with example sentences for false positives and false negatives
2. Given a model's prediction overlaps a gold answer but isn't an exact match, and `use_overlaps=False` (the default)
   - when scoring runs
     - then it is counted as both a false positive *and* a false negative — the strictest possible reading
3. Given `use_cui_doc_limit=True`
   - when scoring runs
     - then a concept's score only counts documents where that concept actually appears in the gold annotations, avoiding false positives from documents annotated before that concept existed in the schema
4. Given `use_groups=True`
   - when scoring runs
     - then concepts are grouped together using `cui2group`, and scores are reported per group — so mix-ups within the same group no longer count as mistakes
5. Given `use_filters=True`
   - when scoring runs
     - then the project's own concept filter is applied, so concepts outside the project's scope aren't scored
6. Given an annotation in the export is marked `irrelevant` or `deleted`
   - when scoring runs
     - then it is handled separately, rather than counted as a correct positive
7. Given `train_supervised_raw(..., print_stats=N, test_size=0)` is used
   - when these statistics are printed
     - then they are actually measured against the training set, because `test_size=0` makes the "test set" and the training set the same data (see US 12)

## Case handling (per-concept tally, with four adjustable rules)

Every prediction is classified against the gold data as a true positive, false positive, or false negative, and tallied separately per concept. The classification rule itself isn't fixed — it depends on the four settings above, each of which can shift the numbers noticeably, and the result returned doesn't record which settings were used. This is the same scoring logic reused by k-fold evaluation (US 20), which is what makes single-pass results and k-fold results comparable to each other. Tests live under `tests/stats/`.

## Later stages (deferred)

- **Results don't record their own settings.** The output is just a plain set of dictionaries; attaching the evaluation settings (and the model's version hash) to the result would make reported numbers easier to reproduce and compare.
- **No precision/recall curve.** Precision and recall are reported at whatever `similarity_threshold` happens to be set at the time. Showing how these numbers change across different thresholds (a PR curve) would be a natural next step, but isn't done yet.
