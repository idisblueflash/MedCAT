# US 13 Model Evaluation via K-Fold Cross-Validation

This specification describes how a user measures a trained model's per-concept precision/recall/F1 quality against a MedCATtrainer export, without needing a separately held-out test set.

## Core Purpose

`get_k_fold_stats(cat, mct_export_data, k=3, ...)` (`medcat/stats/kfold.py`) splits a MedCATtrainer export into `k` folds, evaluates the model against each fold, and aggregates per-CUI precision/recall/F1 metrics (`PerCUIMetrics`) across folds via `get_metrics_mean`, giving a variance-aware quality estimate rather than a single-split snapshot.

## Key Design Consideration

Fold creation is pluggable rather than a single fixed strategy: `SimpleFoldCreator`, `PerDocsFoldCreator`, `PerAnnsFoldCreator`, and `WeightedDocumentsCreator` split by different units (raw examples, whole documents, individual annotations, or document weight), because clinical trainer exports are frequently skewed — a handful of long documents can contain most of the annotations for a rare CUI — and a naive random split could put all of a rare concept's examples in a single fold.

## Acceptance Criteria Summary

The specification requires:
- `get_k_fold_stats` accepts a standard MedCATtrainer export and a configurable `k` without additional data preparation
- Per-CUI metrics are computed independently per fold and then averaged, exposing both the mean and the spread across folds
- The fold-splitting strategy (`SplitType`) is selectable to match how annotations are distributed across the source documents
- Results reuse the same underlying stats machinery (`medcat/stats/stats.py`, `get_stats`) as single-pass evaluation, so k-fold numbers are directly comparable to a non-cross-validated run

## Implementation Notes

Fold creators are selected via `get_fold_creator(mct_export, ...)`; per-fold metrics come from `get_per_fold_metrics`, and cross-fold aggregation from `get_metrics_mean`, all in `medcat/stats/kfold.py`.
