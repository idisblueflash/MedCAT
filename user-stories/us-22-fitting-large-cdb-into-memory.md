# US 22 Fitting a Very Large Concept Database into Memory

As a *deployment engineer running a full UMLS model*, I want to *load a CDB with four million concepts without running out of memory (RAM)*, so that *the model runs on the hardware I actually have, instead of needing a machine sized for its least efficient possible storage layout*.

A CDB is really a collection of separate lookup tables (Python dictionaries), all keyed by the same concept codes (CUIs): `cui2names`, `cui2snames`, `cui2context_vectors`, `cui2count_train`, `cui2tags`, `cui2type_ids`, `cui2preferred_name`, `cui2average_confidence` — eight dictionaries in total. Every one of them stores its own separate copy of every CUI string as a key. With four million concepts, storing the same keys eight times over ends up costing more memory than the actual data.

`perform_optimisation` (`medcat/utils/memory_optimiser.py:241`) fixes this by collapsing all eight dictionaries into one. It creates a single `cui2many` dictionary that maps each CUI to a list of index numbers, and turns each of the old dictionaries into a `DelegatingDict` (`medcat/utils/memory_optimiser.py:67`) — an object that looks up the right index and reads the actual value from one shared array. The CUI strings themselves are now stored only once. The same trick is used for name-keyed dictionaries (`name2many`) and for `snames`.

There's a catch worth knowing: after this optimisation, the CDB is really a *different* internal structure wearing the same outward appearance. `DelegatingDict` behaves just like a normal dictionary from the outside — which is exactly what makes this change invisible to the rest of the codebase. `CDB._memory_optimised_parts` keeps track of which parts have been optimised, and `attempt_fix_after_load` (`:195`) exists because loading an optimised CDB back from disk needs some extra repair steps a normal load doesn't. `unoptimise_cdb` (`:338`) can undo the whole thing. Any code that reaches directly into the CDB's dictionaries and changes them — like training does — has to work correctly whether the CDB is optimised or not, and only the test suite actually guarantees that it does.

## Acceptance Criteria

1. Given a large CDB and a call to `perform_optimisation(cdb)`
   - when it runs
     - then the CUI-keyed dictionaries are replaced with `DelegatingDict`s built on a shared `cui2many` index, so each CUI string is stored only once instead of eight times
2. Given the `optimise_cuis` / `optimise_names` / `optimise_snames` settings
   - when optimisation runs
     - then each group can be optimised on its own, and `_memory_optimised_parts` keeps a record of which ones were
3. Given an optimised CDB
   - when annotation or training code reads `cdb.cui2names[cui]`
     - then it still works exactly as before — the same dictionary-like interface is presented, so nothing calling it needs to change
4. Given an optimised CDB is saved and then reloaded
   - when it is loaded
     - then `attempt_fix_after_load` must run to rebuild the internal delegation structure — without it, the reloaded CDB is broken
5. Given `unoptimise_cdb(cdb)` is called
   - when it runs
     - then the plain, original dictionaries are rebuilt and the optimisation is fully reversed
6. Given a custom encoder/decoder is registered for `DelegatingDict` and `DelegatingSet`
   - when the CDB is saved as JSON (see US 18, `cdb_format='json'`)
     - then the optimised structures survive being saved and loaded again

## Case handling (one shared index, many "view" dictionaries pointing into it)

The approach is: remove duplicate keys, index them once, and make every old dictionary a view into that shared index. The interface stays the same on purpose, so nothing else in the system needs to know this happened. That same transparency is both the strength of the design and its risk: an optimised CDB only behaves correctly to the extent that `DelegatingDict` behaves exactly like a real dictionary, and that's only checked by the test suite. Tests live in `tests/utils/test_memory_optimiser.py`.

## Later stages (deferred)

- **Context vectors themselves aren't compressed.** The single biggest chunk of memory in a trained CDB is `cui2context_vectors` — four arrays of numbers per trained concept — and this optimisation only removes duplicate *keys*, not the vectors' size. Compressing the vectors (through quantisation) would save far more memory than this does.
- **Optimisation has to be triggered manually.** Nothing currently measures a CDB's memory footprint and decides on its own whether to optimise it — the person using it has to know to call this.
