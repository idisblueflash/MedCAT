# US 18 Packaging and Loading Portable Model Packs

As an *MLOps engineer*, I want to *bundle a fully configured pipeline into one portable file and reload it somewhere else*, so that *a model built on one machine works exactly the same way when deployed on another*.

`CAT.create_model_pack(save_dir_path, ...)` (`medcat/cat.py:235`) packs every piece of a running pipeline — the CDB, the vocabulary, the configuration, and any attached MetaCAT, RelCAT, or extra NER models (US 13–15) — into one single `.zip` file, with a version number attached. `CAT.load_model_pack(zip_path, ...)` (`medcat/cat.py:365`) rebuilds an equivalent pipeline from that archive. If you only need the core recognition-and-linking part, you can skip loading the extras individually with separate flags: `load_meta_models` (skip MetaCAT), `load_addl_ner` (skip extra NER models), `load_rel_models` (skip RelCAT).

Two more settings, `force_rehash` and `change_description`, attach a content hash (a fingerprint of the file's contents) and a human-readable note to each pack. This means a model's history and version identity travel along with the file itself, instead of depending on filenames or a separate changelog that could drift out of sync with the actual file.

## Acceptance Criteria

1. Given a model pack created on one machine
   - when it is loaded on a different machine
     - then it produces identical entity-extraction behaviour
2. Given a caller only needs the core recognition-and-linking parts
   - when the selective-loading flags are set
     - then MetaCAT, RelCAT, and extra-NER weights are skipped, keeping the load fast and light
3. Given some configuration needs to change at deployment time
   - when `medcat_config_dict` / `meta_cat_config_dict` / `ner_config_dict` are passed in while loading
     - then those settings are overridden without needing to modify the archive itself
4. Given a model pack is being created
   - when `cdb_format` is set (`dill` by default)
     - then the CDB's storage format inside the pack is explicit and can be changed

## Case handling (pack everything, fingerprint it, then load selectively)

Creating a pack takes a snapshot of every component plus some environment details, and stamps it with a content hash. Loading does the reverse, respecting the selective-loading flags and any config overrides you pass in. The packaging and versioning logic lives in `medcat/utils/saving/` (`serializer.py`, `converter.py`, `envsnapshot.py`).

## Later stages (deferred)

- **No cryptographic signature.** Packs carry a content hash (which detects accidental changes) but no cryptographic signature (which would prove who actually created the file).
- **No formal compatibility chart.** Guarantees about which pack versions load on which library versions are informal today; a documented compatibility table would make this clearer.
