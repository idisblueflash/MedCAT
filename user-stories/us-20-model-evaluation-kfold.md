# US 20 Model Evaluation via K-Fold Cross-Validation

As an *ML engineer*, I want to *measure per-concept precision, recall, and F1 using cross-validation*, so that *I get a quality estimate that also shows how much the numbers vary, without needing to hold out a separate test set*.

("K-fold cross-validation" is a way to test a model fairly using all your data: you split the data into `k` roughly equal parts, called "folds," and repeatedly test on one fold while using the model as-is. It gives you several scores instead of just one, so you can see how much the score varies, not just its average.)

`get_k_fold_stats(cat, mct_export_data, k=3, ...)` (`medcat/stats/kfold.py`) splits a MedCATtrainer export into `k` folds, evaluates the model against each fold, and combines the per-concept metrics (`PerCUIMetrics`) across all folds using `get_metrics_mean`. This gives you an estimate that shows how much the score spreads out, not just a single snapshot number from one split.

How the folds are created isn't fixed — you can choose between several strategies: `SimpleFoldCreator`, `PerDocsFoldCreator`, `PerAnnsFoldCreator`, and `WeightedDocumentsCreator`. Each one splits the data by a different unit: raw examples, whole documents, individual annotations, or documents weighted by size. This matters because clinical exports are often lopsided — a handful of very long documents might hold most of the examples for a rare concept. Splitting purely at random could accidentally leave all of that rare concept's examples in just one fold, which would badly skew the results.

## Acceptance Criteria

1. Given a standard MedCATtrainer export and a chosen number of folds (`k`)
   - when `get_k_fold_stats` runs
     - then it evaluates the model with no extra data preparation needed
2. Given the `k` folds have been evaluated
   - when the metrics are combined
     - then per-concept metrics are computed for each fold and then averaged, showing both the average and how much it varies
3. Given annotations are spread unevenly across documents
   - when a fold-splitting strategy (`SplitType`) is chosen
     - then the splitting method can be matched to that uneven distribution
4. Given a k-fold run and a single-pass run (US 19)
   - when their results are compared
     - then they're directly comparable, because both reuse the exact same scoring logic (`medcat/stats/stats.py`, `get_stats`)

## Case handling (choose a split method, score each fold, then average)

A fold-creation method splits the export by whichever unit you chose. Each fold is then scored using the same shared scoring logic used elsewhere, and the results are averaged across all folds. Fold creators are selected through `get_fold_creator(mct_export, ...)`; per-fold metrics come from `get_per_fold_metrics`, and combining them across folds comes from `get_metrics_mean` — all found in `medcat/stats/kfold.py`.

## Later stages (deferred)

- **No stratified folds by concept.** The current split strategies balance by document or annotation count, not by how many examples of each specific concept end up in each fold. Splitting to balance rare concepts specifically would make their scores more stable.
- **No confidence intervals.** The output currently gives an average and a spread, but not a formal confidence interval — adding one would make comparing different models more rigorous.
