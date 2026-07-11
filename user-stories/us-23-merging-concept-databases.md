# US 23 Merging Two Concept Databases

As a *model builder combining a hospital-specific model with a public one*, I want to *merge two CDBs into one*, so that *I keep the training both of them accumulated rather than throwing one away or retraining from scratch*.

Two CDBs may each carry expensive, non-reproducible learning: months of self-supervised training (US 10) and irreplaceable human annotation (US 11, US 12), both living as context vectors and training counts inside the CDB. `merge_cdb` (`medcat/utils/cdb_utils.py:10`) produces a third, new CDB from two inputs, leaving both untouched. Concepts unique to either side are copied across. Concepts present in both are the interesting case: names and type ids are unioned, and the context vectors are combined — weighted by each side's `cui2count_train`, so a concept the first CDB saw ten thousand times and the second saw twice is not dragged halfway toward the second's representation (`overwrite_training` tunes this precedence).

The risk is that a merged CDB is coherent only if the two sides shared a *vocabulary*. Context vectors are averages of word embeddings drawn from a `Vocab` (US 03). Two CDBs trained against different vocabs have vectors in different embedding spaces, and averaging them is arithmetic on incommensurable numbers — it produces a vector, it produces no error, and the resulting similarity scores are noise. Nothing in `merge_cdb` checks that the two CDBs were trained against the same vocab, because the CDB does not record which vocab it was trained with.

## Acceptance Criteria

1. Given two CDBs and `merge_cdb(cdb1, cdb2)`
   - when it runs
     - then a new CDB is returned and neither input is modified
2. Given a CUI present in only one input
   - when merging runs
     - then it is copied across with its names, vectors, counts, and type ids intact
3. Given a CUI present in both
   - when merging runs
     - then names, snames, and type ids are unioned, and context vectors are combined weighted by each side's training count
4. Given a name that maps to different CUIs in each CDB
   - when merging runs
     - then it becomes ambiguous in the merged CDB — mapping to both — and its resolution is deferred to context (US 06), exactly as in US 06
5. Given the two CDBs were trained against different vocabularies
   - when merging runs
     - then their context vectors are averaged anyway, silently, producing a model whose similarity scores are meaningless
6. Given conflicting `name2cuis2status` for the same `(name, cui)`
   - when merging runs
     - then one side's status wins, and the model's disambiguation behaviour for that name changes accordingly

## Case handling (union the names, weight the vectors)

Merging is set union on the lookup structures and a count-weighted average on the learnt state. It is a purely mechanical combination: no validation that the two models are compatible, no reconciliation of conflicting statuses beyond a precedence rule, no report of what conflicted. Coverage lives in `tests/utils/test_cdb_utils.py`.

## Later stages (deferred)

- **No vocab compatibility check.** The CDB does not record the vocab it was trained against, so the one precondition that makes vector merging meaningful cannot even be tested. Storing a vocab hash in the CDB would fix this.
- **No merge report.** How many CUIs overlapped, how many names became newly ambiguous, how many statuses conflicted — all knowable, none reported.
