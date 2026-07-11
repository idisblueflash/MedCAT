# US 08 Packaging and Loading Portable Model Packs

As an *MLOps engineer*, I want to *bundle a configured pipeline into one portable archive and reload it elsewhere*, so that *a model built on one machine deploys identically on another*.

`CAT.create_model_pack(save_dir_path, ...)` (`medcat/cat.py:235`) bundles every component of the running pipeline — CDB, vocabulary, config, and any attached MetaCAT/RelCAT/NER models — into a single versioned `.zip`. `CAT.load_model_pack(zip_path, ...)` (`medcat/cat.py:365`) reconstructs an equivalent pipeline from that archive, with independent flags to skip MetaCAT models (`load_meta_models`), additional NER (`load_addl_ner`), or RelCAT models (`load_rel_models`) when only core NER+L is needed.

`force_rehash` and `change_description` tie a content hash and a human-readable note to each pack, so a model's provenance and version identity travel with the artifact itself rather than depending on filename conventions or external changelogs that drift out of sync with the file.

## Acceptance Criteria

1. Given a model pack created on one machine
   - when it is loaded on another
     - then it reproduces identical entity-extraction behaviour
2. Given a caller needs only core NER+L
   - when selective loading flags are set
     - then MetaCAT / RelCAT / additional-NER weights are skipped, keeping the load fast and light
3. Given configuration must change at deploy time
   - when `medcat_config_dict` / `meta_cat_config_dict` / `ner_config_dict` are passed at load
     - then config is overridden without modifying the archive
4. Given a model pack is created
   - when `cdb_format` is set (default `dill`)
     - then the CDB serialization format inside the pack is explicit and controllable

## Case handling (bundle / rehash / selective load)

Creation snapshots every component plus environment metadata and stamps a content hash; loading reverses this, honouring the selective-load flags and any config overrides. Packaging and versioning logic lives in `medcat/utils/saving/` (`serializer.py`, `converter.py`, `envsnapshot.py`).

## Later stages (deferred)

- **Signature/verification.** Packs carry a content hash but no cryptographic signature; signing would let consumers verify provenance, not just detect drift.
- **Backward-compat matrix.** Cross-version load guarantees are informal; a documented compatibility matrix would clarify which pack versions load on which library versions.
