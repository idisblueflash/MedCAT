# US 12 Incrementally Correcting a Live Model

As a *clinical curator*, I want to *fix a specific known mistake in a running model*, so that *a missing name, wrong link, or ungrouped concept is corrected immediately without a full retraining pass*.

`CAT.add_cui_to_group(cui, group_name)` (`medcat/cat.py:676`), `CAT.unlink_concept_name(cui, name, ...)` (`medcat/cat.py:693`), and `CAT.add_and_train_concept(cui, name, ...)` (`medcat/cat.py:730`) apply a single targeted correction directly to the loaded model, effective on the very next `get_entities` call, with no reload or rebuild.

The key safety property: `unlink_concept_name` does not delete the CUI — it removes only the name-to-CUI link, so the name is never again linked to that CUI while the concept and its other names stay intact. A wrong *name* mapping is a much narrower and more common mistake than a wrong *concept*, and the API is deliberately scoped to fix the former without collateral damage to the latter.

## Acceptance Criteria

1. Given a name that should link to a CUI
   - when `add_and_train_concept` is called
     - then the name's context vector is trained immediately, optionally from a real spaCy doc/span rather than a synthetic one
2. Given a name is wrongly linked to a CUI
   - when `unlink_concept_name` is called
     - then future detection of that name for that CUI stops, while the CUI and its other names remain
3. Given several related concepts
   - when `add_cui_to_group` groups them (stored in `cdb.addl_info['cui2group']`)
     - then they can be filtered or reported on together
4. Given any of these corrections is applied
   - when the next annotation call runs
     - then the change is visible without a model-pack reload

## Case handling (targeted CDB edits)

Each operation mutates a narrow slice of CDB state — a name link, a trained vector, or a group membership — and takes effect on the next call. Live edits are captured through `medcat/utils/cdb_state.py` (`captured_state_cdb`), so a modified CDB can be checkpointed or rolled back the same way a training run can.

## Later stages (deferred)

- **Edit audit trail.** Corrections mutate state in place; a recorded log of who changed what would aid review and reproducibility.
- **Bulk correction.** The API is per-concept; a batch interface would scale curated fix-lists without scripting one call each.
