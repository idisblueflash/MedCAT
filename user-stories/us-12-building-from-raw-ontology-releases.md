# US 12 Building CDB and Vocab from Raw UMLS/SNOMED-CT Releases

This specification describes how a user with a licensed UMLS or SNOMED-CT release, but no pre-built MedCAT model, produces a usable CDB and Vocab from the raw ontology files.

## Core Purpose

`medcat/utils/preprocess_umls.py` and `medcat/utils/preprocess_snomed.py` convert the respective official release formats (UMLS RRF files, SNOMED-CT RF2 files) into the flat CSV schema `CDBMaker` expects. `medcat/utils/model_creator.py` then drives an end-to-end build — combining a `concept_csv_file` with an `unsupervised_training_data_file` and an optional `medcat_config_file` — into a finished CDB and Vocab, runnable directly as `python medcat/utils/model_creator.py <config.yml>`.

## Key Design Consideration

Parsing a specific ontology's release format is kept separate from the general CDB-building pipeline, so the same `CDBMaker`/`model_creator` machinery works for UMLS, SNOMED-CT, or any custom ontology, as long as it has first been flattened into the common `cui`/`name`/`ontologies`/`name_status`/`type_ids` CSV schema (US 02). This avoids duplicating the CDB/Vocab-building logic per ontology vendor.

## Acceptance Criteria Summary

The specification requires:
- `unigram_table_size` is configurable so a small test corpus doesn't have to allocate the 100,000,000-entry default table
- The CDB and Vocab produced by `model_creator` load with `CDB.load` / `Vocab.load` exactly like the officially distributed UMLS/SNOMED-CT model packs
- An optional `medcat_config_file` allows adjusting MedCAT properties (see `configs/`, `medcat/config.py`) as part of the same build step
- A working example configuration exists (`tests/model_creator/config_example.yml`) that can be run as-is to validate the toolchain

## Implementation Notes

`tests/model_creator/umls_sample.csv` documents the expected intermediate CSV schema end-to-end, connecting the ontology-specific preprocessors to the general-purpose CDB build described in US 02.
