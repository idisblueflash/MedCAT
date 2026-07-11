# US 11 Incrementally Correcting a Live Model

This specification describes how a user fixes a specific, known mistake in a running MedCAT model — a missing name, a wrong link, an ungrouped concept — without running a full retraining pass.

## Core Purpose

`CAT.add_cui_to_group(cui, group_name)` (`medcat/cat.py:676`), `CAT.unlink_concept_name(cui, name, ...)` (`medcat/cat.py:693`), and `CAT.add_and_train_concept(cui, name, ...)` (`medcat/cat.py:730`) let a user apply a single targeted correction directly to the loaded model, effective on the very next `get_entities` call, without reloading or rebuilding the model pack.

## Key Design Consideration

`unlink_concept_name` does not delete the CUI from the CDB — it removes only the name-to-CUI link, so "medcat will never again link the name to this CUI" while the concept and its other names remain fully intact. This distinction matters because a wrong *name* mapping is a much narrower and more common mistake than a wrong *concept*, and the API is deliberately scoped to fix the former without collateral damage to the latter.

## Acceptance Criteria Summary

The specification requires:
- Adding a name via `add_and_train_concept` immediately trains that name's context vector, optionally using a real spaCy document/span as context rather than a synthetic one
- Unlinking a name stops future detection of that name for the given CUI without removing the CUI or its other names
- Grouping CUIs via `add_cui_to_group` (stored in `cdb.addl_info['cui2group']`) allows multiple related concepts to be filtered or reported on together
- Corrections are visible to subsequent annotation calls without requiring a model pack reload

## Implementation Notes

Live edits are captured through `medcat/utils/cdb_state.py` (`captured_state_cdb`), which allows the modified CDB state to be checkpointed or rolled back the same way a training run can be.
