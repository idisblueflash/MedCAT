# US 12 Incrementally Correcting a Live Model

As a *clinical curator*, I want to *fix one specific, known mistake in a model that's already running*, so that *a missing name, a wrong link, or an ungrouped concept gets corrected right away, without a full retraining pass*.

Three methods let you make a small, targeted fix directly on a loaded model, and the fix takes effect the very next time you call `get_entities` — no reload, no rebuild:

- `CAT.add_cui_to_group(cui, group_name)` (`medcat/cat.py:676`)
- `CAT.unlink_concept_name(cui, name, ...)` (`medcat/cat.py:693`)
- `CAT.add_and_train_concept(cui, name, ...)` (`medcat/cat.py:730`)

The important safety detail: `unlink_concept_name` does not delete the concept itself — it only removes the link between one specific name and that concept. So the name will never again point to that concept, but the concept and all its other names stay exactly as they were. A wrong *name-to-concept link* is a much smaller and much more common mistake than "this concept is wrong," so this tool is deliberately scoped just to fix the name-link problem, without any risk of damaging the concept itself.

## Acceptance Criteria

1. Given a name that should be linked to a concept
   - when `add_and_train_concept` is called
     - then that name's context vector is trained right away — optionally using a real sentence you provide, instead of a made-up one
2. Given a name is wrongly linked to a concept
   - when `unlink_concept_name` is called
     - then that name will never again be detected as meaning that concept, while the concept itself and its other names are untouched
3. Given several related concepts
   - when `add_cui_to_group` groups them together (stored in `cdb.addl_info['cui2group']`)
     - then they can later be filtered or reported on as one group
4. Given any of these three fixes has been applied
   - when the next annotation call runs
     - then the change is already visible — there's no need to reload the model pack

## Case handling (small, direct edits to the CDB)

Each of these operations only changes one narrow piece of the CDB — one name link, one trained vector, or one group membership — and the change applies from the very next call onward. Live edits like these are tracked through `medcat/utils/cdb_state.py` (`captured_state_cdb`), so a changed CDB can be saved as a checkpoint or rolled back, the same way a training run can be.

## Later stages (deferred)

- **No audit trail for edits.** These corrections change the model's state directly, in place. A recorded log of who changed what, and when, would make review and reproducing results easier.
- **No bulk-correction tool.** Right now each fix has to be applied one concept at a time. A batch version would make it easier to apply a long list of curated fixes without writing a separate call for each one.
