# US 22 Fitting a Very Large Concept Database into Memory

As a *deployment engineer running a full UMLS model*, I want to *load a four-million-concept CDB without exhausting RAM*, so that *the model runs on the hardware I actually have rather than requiring a machine sized for its most wasteful representation*.

The CDB is a pile of parallel dictionaries all keyed by the same things: `cui2names`, `cui2snames`, `cui2context_vectors`, `cui2count_train`, `cui2tags`, `cui2type_ids`, `cui2preferred_name`, `cui2average_confidence` — eight dicts, each storing its own copy of every CUI string as a key. At four million concepts, the keys cost more than the values. `perform_optimisation` (`medcat/utils/memory_optimiser.py:241`) collapses them: one `cui2many` dict maps each CUI to a list of indices, and each former dict becomes a `DelegatingDict` (`medcat/utils/memory_optimiser.py:67`) that looks up the index and reads the value out of a shared array. The CUI strings are stored once. The same trick applies to the name-keyed dicts (`name2many`) and to `snames`.

The risk is that the optimised CDB is a *different object graph* wearing the same interface. `DelegatingDict` quacks like a dict, which is what makes this transparent — and means the optimisation is invisible at the call sites that depend on it. `CDB._memory_optimised_parts` records which parts are optimised, and `attempt_fix_after_load` (`:195`) exists precisely because loading an optimised CDB needs repair steps a normal load does not. `unoptimise_cdb` (`:338`) reverses it. Code that reaches into the CDB's dicts and mutates them directly — as training does — must work correctly against both representations, and only the tests guarantee it does.

## Acceptance Criteria

1. Given a large CDB and `perform_optimisation(cdb)`
   - when it runs
     - then the CUI-keyed dicts are replaced by `DelegatingDict`s over a shared `cui2many` index, and each CUI string is stored once rather than eight times
2. Given `optimise_cuis` / `optimise_names` / `optimise_snames` flags
   - when optimisation runs
     - then each group can be optimised independently, and `_memory_optimised_parts` records which were
3. Given an optimised CDB
   - when annotation or training reads `cdb.cui2names[cui]`
     - then it still works — the same dict interface is presented, so calling code is unchanged
4. Given an optimised CDB is saved and reloaded
   - when it is loaded
     - then `attempt_fix_after_load` must run to restore the delegation structure; without it the reloaded CDB is malformed
5. Given `unoptimise_cdb(cdb)`
   - when it runs
     - then the plain dicts are reconstructed and the optimisation fully reversed
6. Given a custom encoder/decoder registered for `DelegatingDict` and `DelegatingSet`
   - when the CDB is serialised as JSON (US 18, `cdb_format='json'`)
     - then the optimised structures survive the round trip

## Case handling (one index, many delegating views)

Deduplicate the keys, index them once, and make every former dict a view. The interface is preserved so that nothing else in the system needs to know. That transparency is the design's strength and its exposure: an optimised CDB is correct exactly to the degree that `DelegatingDict` is a faithful dict, and that faithfulness is asserted only by tests. Coverage lives in `tests/utils/test_memory_optimiser.py`.

## Later stages (deferred)

- **Context vectors are not compressed.** The largest single memory consumer in a trained CDB is `cui2context_vectors` — four float arrays per trained concept — and this optimisation dedupes only its *keys*. Quantising the vectors would dwarf the saving achieved here.
- **Optimisation is manual.** Nothing measures the CDB's footprint and decides; the caller must know to do this.
