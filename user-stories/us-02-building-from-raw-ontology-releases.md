# US 02 Building CDB and Vocab from Raw UMLS/SNOMED-CT Releases

As a *knowledge engineer*, I want to *turn a licensed raw ontology release into a usable CDB and Vocab*, so that *I can build a MedCAT model from UMLS or SNOMED-CT even when no pre-built pack exists*.

`medcat/utils/preprocess_umls.py` and `medcat/utils/preprocess_snomed.py` convert the official release formats (UMLS RRF, SNOMED-CT RF2) into the flat CSV schema `CDBMaker` expects. `medcat/utils/model_creator.py` then drives an end-to-end build — combining a `concept_csv_file`, an `unsupervised_training_data_file`, and an optional `medcat_config_file` — into a finished CDB and Vocab, runnable as `python medcat/utils/model_creator.py <config.yml>`.

Parsing a specific vendor's release format is kept separate from the general CDB build, so the same `CDBMaker` / `model_creator` machinery serves UMLS, SNOMED-CT, or any custom ontology once flattened into the common `cui`/`name`/`ontologies`/`name_status`/`type_ids` schema (US 01). This avoids duplicating the build logic per ontology.

## Acceptance Criteria

1. Given a small test corpus
   - when `unigram_table_size` is configured
     - then the build need not allocate the 100,000,000-entry default table
2. Given a CDB and Vocab produced by `model_creator`
   - when they are loaded with `CDB.load` / `Vocab.load`
     - then they behave exactly like the officially distributed UMLS/SNOMED-CT model packs
3. Given MedCAT properties must be adjusted for the build
   - when an optional `medcat_config_file` is supplied (see `configs/`, `medcat/config.py`)
     - then those properties are applied as part of the same build step
4. Given a new user validating the toolchain
   - when they run the example config (`tests/model_creator/config_example.yml`)
     - then it runs as-is end to end

## Case handling (vendor preprocess → shared build)

A vendor-specific preprocessor flattens the raw release to the common CSV schema; from there the shared `CDBMaker` / `model_creator` path builds CDB and Vocab identically regardless of source. `tests/model_creator/umls_sample.csv` documents the expected intermediate schema, connecting the preprocessors to the general build of US 01.

## Later stages (deferred)

- **Additional vendors.** Only UMLS and SNOMED-CT preprocessors ship; a documented adapter contract would ease adding new ontology formats.
- **Incremental rebuilds.** A release upgrade currently rebuilds from scratch; diffing against the prior release would avoid reprocessing unchanged concepts.
