# US 02 Building CDB and Vocab from Raw UMLS/SNOMED-CT Releases

As a *knowledge engineer*, I want to *turn an official, licensed ontology release into a usable CDB and Vocab*, so that *I can build a MedCAT model from UMLS or SNOMED-CT even when no ready-made model pack exists*.

UMLS and SNOMED-CT are large medical vocabularies. When you download them from the official source, the files come in the vendor's own format, not the simple CSV format MedCAT expects (US 01). Two helper scripts fix this:

- `medcat/utils/preprocess_umls.py` converts the UMLS release format (called RRF) into the flat CSV shape MedCAT wants.
- `medcat/utils/preprocess_snomed.py` does the same for SNOMED-CT's release format (called RF2).

Once the CSV is ready, `medcat/utils/model_creator.py` builds everything end to end. It takes three things — the concept CSV file, a file of unsupervised training text, and an optional MedCAT config file — and turns them into a finished CDB and Vocab. You run it as a single command:
`python medcat/utils/model_creator.py <config.yml>`

The step that reads a vendor's specific file format is kept separate from the general build step. This means the same `CDBMaker` / `model_creator` tools work for UMLS, SNOMED-CT, or any other ontology, as long as it's first flattened into the common `cui`/`name`/`ontologies`/`name_status`/`type_ids` columns from US 01. Nobody has to write the build logic again for each new vocabulary.

## Acceptance Criteria

1. Given a small test corpus
   - when `unigram_table_size` is set to a smaller number
     - then the build does not have to create the default 100,000,000-entry table, which would be wasteful for a small test
2. Given a CDB and Vocab produced by `model_creator`
   - when they are loaded with `CDB.load` / `Vocab.load`
     - then they behave exactly like the official, ready-made UMLS/SNOMED-CT model packs
3. Given some MedCAT settings need to be changed for this build
   - when an optional config file is supplied (see `configs/`, `medcat/config.py`)
     - then those settings are applied as part of the same build
4. Given a new user trying the toolchain for the first time
   - when they run the example config file (`tests/model_creator/config_example.yml`)
     - then it runs from start to finish without changes

## Case handling (vendor format → shared build)

A vendor-specific script flattens the raw release into the common CSV shape. From there, the same shared `CDBMaker` / `model_creator` path builds the CDB and Vocab the same way, no matter which ontology it came from. `tests/model_creator/umls_sample.csv` shows the expected in-between format, connecting the vendor scripts to the general build described in US 01.

## Later stages (deferred)

- **More vendors.** Only UMLS and SNOMED-CT have ready-made preprocessors. Writing down a clear "adapter contract" would make it easier to add other ontology formats.
- **Incremental rebuilds.** Right now, upgrading to a new release means rebuilding everything from scratch. Comparing against the previous release and only reprocessing what changed would save time.
