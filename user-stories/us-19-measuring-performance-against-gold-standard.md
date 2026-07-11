# US 19 Measuring Performance Against a Gold Standard

As a *model builder deciding whether to deploy*, I want to *know the precision, recall, and F1 per concept, with worked examples of the model's mistakes*, so that *I can judge whether it is good enough — and see which concepts it is bad at, because an aggregate F1 hides everything that matters*.

`get_stats(cat, data)` (`medcat/stats/stats.py:272`) replays a MedCATtrainer export: it annotates each document with the model, compares against the human annotations, and accumulates true positives, false positives, and false negatives **per CUI**. From those it derives per-concept precision, recall, and F1, plus `cui_counts`, plus — the part that earns its keep — `examples`, a dict of actual FP and FN sentences per concept. A recall of 0.6 is not actionable; twenty false-negative sentences for that CUI tell you the model is missing an abbreviation.

The risks are all in what counts as a match, and each is a switch. `use_overlaps` (`:24`) decides whether an overlapping-but-not-identical span counts. `use_cui_doc_limit` (`:25`) restricts a CUI's metrics to documents where that CUI was actually annotated — which matters enormously if the annotation schema changed mid-project, since otherwise every document annotated before the concept was added contributes false positives. `use_groups` reports on concept *groups* rather than CUIs, which makes numbers look better by forgiving within-group confusions. And `use_filters` applies the project's own CUI filter (US 08). None of these are recorded alongside the result: two F1 numbers from this function are not comparable unless you know all four settings.

## Acceptance Criteria

1. Given a model and a gold-standard export
   - when `get_stats` runs
     - then per-CUI `tp`, `fp`, `fn`, `precision`, `recall`, `f1`, and `cui_counts` are returned, along with FP/FN example sentences per concept
2. Given a model prediction overlapping a gold span but not matching it exactly, and `use_overlaps=False` (the default)
   - when scoring runs
     - then it counts as both a false positive and a false negative — the harshest reading
3. Given `use_cui_doc_limit=True`
   - when scoring runs
     - then a CUI's metrics only count documents in which that CUI appears in the gold annotations, suppressing false positives from documents annotated before the concept entered the schema
4. Given `use_groups=True`
   - when scoring runs
     - then concepts are collapsed into their `cui2group` and metrics reported per group — confusions within a group stop being errors
5. Given `use_filters=True`
   - when scoring runs
     - then the project's own CUI filter is applied, so concepts outside the project's scope are not scored against it
6. Given an annotation marked `irrelevant` or `deleted` in the export
   - when scoring runs
     - then it is handled separately rather than being scored as a positive
7. Given `train_supervised_raw(..., print_stats=N, test_size=0)`
   - when these statistics are printed
     - then they are computed against the training set, because `test_size=0` makes the test set and train set the same object (US 12)

## Case handling (per-CUI tally, four switches on what counts)

Every prediction is classified against the gold set as TP, FP, or FN and tallied per concept. The classification rule is not fixed — it is parameterised by four flags that each move the number, sometimes substantially, and the returned tuple carries no record of which were set. This is the same stats machinery k-fold evaluation reuses (US 20), which is what makes single-pass and k-fold numbers directly comparable. Coverage lives under `tests/stats/`.

## Later stages (deferred)

- **Metrics are unlabelled.** The output is a bare tuple of dicts; attaching the evaluation settings (and the model hash) to the result would make reported numbers reproducible and comparable.
- **No confidence-threshold sweep.** Precision and recall are reported at whatever `similarity_threshold` happens to be configured; a PR curve over that threshold is the natural thing to want and is not produced.
