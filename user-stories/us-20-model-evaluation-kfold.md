# US 20 Model Evaluation via K-Fold Cross-Validation

As an *ML engineer*, I want to *measure per-concept precision/recall/F1 with cross-validation*, so that *I get a variance-aware quality estimate from a trainer export without holding out a separate test set*.

`get_k_fold_stats(cat, mct_export_data, k=3, ...)` (`medcat/stats/kfold.py`) splits a MedCATtrainer export into `k` folds, evaluates the model against each, and aggregates per-CUI metrics (`PerCUIMetrics`) across folds via `get_metrics_mean` — giving a spread-aware estimate rather than a single-split snapshot.

Fold creation is pluggable rather than fixed: `SimpleFoldCreator`, `PerDocsFoldCreator`, `PerAnnsFoldCreator`, and `WeightedDocumentsCreator` split by different units (raw examples, whole documents, individual annotations, document weight). Clinical exports are frequently skewed — a handful of long documents can hold most annotations for a rare CUI — so a naive random split could strand all of a rare concept's examples in one fold.

## Acceptance Criteria

1. Given a standard MedCATtrainer export and a chosen `k`
   - when `get_k_fold_stats` runs
     - then it evaluates with no additional data preparation
2. Given the k folds are evaluated
   - when metrics are aggregated
     - then per-CUI metrics are computed per fold and averaged, exposing both mean and spread
3. Given annotations are distributed unevenly across documents
   - when a `SplitType` is selected
     - then the fold-splitting strategy can be matched to that distribution
4. Given a k-fold run and a single-pass run
   - when their numbers are compared
     - then they are directly comparable, because both reuse the same stats machinery (`medcat/stats/stats.py`, `get_stats`)

## Case handling (pluggable split → per-fold stats → mean)

A fold creator partitions the export by the chosen unit, each fold is scored with the shared stats path, and results are averaged across folds. Fold creators are selected via `get_fold_creator(mct_export, ...)`; per-fold metrics come from `get_per_fold_metrics` and cross-fold aggregation from `get_metrics_mean`, all in `medcat/stats/kfold.py`.

## Later stages (deferred)

- **Stratified folds.** Split strategies target the annotation unit, not label balance; per-CUI stratification would stabilise metrics for rare concepts.
- **Confidence intervals.** Output exposes mean and spread; reporting explicit CIs would make cross-model comparison more rigorous.
