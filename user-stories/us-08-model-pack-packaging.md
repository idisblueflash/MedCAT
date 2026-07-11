# US 08 Packaging and Loading Portable Model Packs

This specification describes how a fully configured MedCAT pipeline — CDB, vocabulary, config, and any attached MetaCAT/RelCAT/NER models — is turned into a single portable artifact that can be shared and deployed elsewhere.

## Core Purpose

`CAT.create_model_pack(save_dir_path, ...)` (`medcat/cat.py:235`) bundles every component of the running pipeline into a single versioned `.zip`. `CAT.load_model_pack(zip_path, ...)` (`medcat/cat.py:365`) reconstructs an equivalent pipeline from that archive on a different machine, with independent flags to skip loading MetaCAT models (`load_meta_models`), additional NER components (`load_addl_ner`), or RelCAT models (`load_rel_models`) when a caller only needs core NER+L.

## Key Design Consideration

`force_rehash` and `change_description` tie a content hash and a human-readable note to each pack, so a model's provenance and version identity travel with the artifact itself rather than depending on filename conventions or external changelogs that can drift out of sync with the actual file.

## Acceptance Criteria Summary

The specification requires:
- A model pack created on one machine reproduces identical entity extraction behaviour when loaded on another
- Selective loading flags avoid pulling in MetaCAT, RelCAT, or additional NER weights when they aren't needed, keeping lightweight deployments fast to load
- `medcat_config_dict`, `meta_cat_config_dict`, and `ner_config_dict` allow overriding configuration at load time without modifying the archive itself
- The CDB serialization format inside the pack is explicit and controllable (`cdb_format`, default `dill`)

## Implementation Notes

Packaging and versioning logic lives in `medcat/utils/saving/` (`serializer.py`, `converter.py`, `envsnapshot.py`), which also captures environment metadata alongside the model artifacts.
