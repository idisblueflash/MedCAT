# US 23 Merging Two Concept Databases

As a *model builder combining a hospital-specific model with a public one*, I want to *merge two CDBs into one*, so that *I keep the training progress both of them have already accumulated, instead of throwing one away or retraining everything from scratch*.

Two separate CDBs might each hold expensive, hard-to-reproduce learning: months of unsupervised training (US 10) and irreplaceable human-checked corrections (US 11, US 12), all stored inside the CDB as context vectors and training counts. `merge_cdb` (`medcat/utils/cdb_utils.py:10`) produces a brand-new, third CDB from the two you give it, leaving both original CDBs untouched.

Concepts that only exist in one of the two CDBs get simply copied across. Concepts that exist in *both* are the interesting case: their names and type IDs get combined (union), and their context vectors get combined too — weighted by how many times each side actually saw the concept during training (`cui2count_train`). So if the first CDB saw a concept ten thousand times and the second saw it only twice, the merged vector stays close to the first one's, instead of being dragged halfway toward the second (the setting `overwrite_training` controls exactly how this weighting works).

Here's the risk: a merged CDB only makes sense if both original CDBs were trained using the *same vocabulary* (US 03). Context vectors are just averages of word embeddings drawn from a specific `Vocab`. If the two CDBs were trained against different vocabularies, their vectors live in completely different, incompatible number spaces — averaging them still produces a vector and no error message, but the resulting similarity scores are essentially meaningless noise. `merge_cdb` currently has no way to check for this, because a CDB doesn't record which vocabulary it was trained with in the first place.

## Acceptance Criteria

1. Given two CDBs and a call to `merge_cdb(cdb1, cdb2)`
   - when it runs
     - then a new CDB is returned, and neither of the original two is changed
2. Given a concept exists in only one of the two CDBs
   - when merging runs
     - then it is copied across with its names, vectors, counts, and type IDs intact
3. Given a concept exists in both CDBs
   - when merging runs
     - then names, alternate names, and type IDs are combined, and the context vectors are combined using each side's training count as a weight
4. Given the same name maps to different concepts in each of the two CDBs
   - when merging runs
     - then that name becomes ambiguous in the merged CDB — pointing to both concepts — and deciding which one is meant is left to the context model, exactly as in US 06
5. Given the two CDBs were trained using different vocabularies
   - when merging runs
     - then their context vectors are still averaged together anyway, silently, producing a model whose similarity scores don't mean anything reliable
6. Given the two CDBs disagree about the status (`name2cuis2status`) of the same name-concept pair
   - when merging runs
     - then one side's status simply wins, and the merged model's decisions about that name change accordingly

## Case handling (combine the names, weight-average the vectors)

Merging works by taking the union of all the lookup information, and a count-weighted average of the learned vectors. It's a purely mechanical combination: there's no check that the two models are actually compatible, no resolution of conflicting statuses beyond "one side wins," and no report of what conflicted along the way. Tests live in `tests/utils/test_cdb_utils.py`.

## Later stages (deferred)

- **No check for matching vocabularies.** A CDB doesn't currently record which vocabulary it was trained against, so the one condition that makes vector-merging meaningful can't even be checked. Storing a vocabulary "fingerprint" (hash) in the CDB would fix this.
- **No merge summary report.** Useful information — how many concepts overlapped, how many names became newly ambiguous, how many statuses conflicted — is all knowable during the merge, but none of it is currently reported back to the user.
