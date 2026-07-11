# US 01 Building a Concept Database from a CSV

As a *knowledge engineer*, I want to *turn a flat list of concepts into a Concept Database (CDB)*, so that *MedCAT's NER+L pipeline can recognise and link the entities I care about*.

`CDBMaker.prepare_csvs` (`medcat/cdb_maker.py`) ingests one or more CSV files where each row provides a `cui` and a `name`, optionally alongside `ontologies`, `name_status`, `type_ids`, and `description`. A concept with multiple synonyms appears as multiple rows sharing the same `cui`, which the maker merges into a single `CDB` entry with all known names attached.

The one field worth care is `name_status`: `P` marks a preferred name that should resolve to this concept in the large majority of occurrences, `N` forces the name through disambiguation, and `A` lets MedCAT decide from training data. Getting it wrong for a few rows has little impact, so the format tolerates it being omitted or approximate rather than requiring it exhaustively correct up front.

## Acceptance Criteria

1. Given several CSV rows sharing one `cui`
   - when `prepare_csvs` builds the CDB
     - then they are merged into a single concept with every name retained
2. Given a CSV that supplies only `cui` and `name`
   - when the CDB is built
     - then it succeeds — all other columns are optional and may appear on just one row per concept to keep files small
3. Given a built CDB
   - when it is saved with `CDB.save` and reloaded with `CDB.load`
     - then names, ontology tags, and type IDs survive the round trip unchanged
4. Given malformed or duplicate rows
   - when the CSV is ingested
     - then they are reported rather than silently corrupting the resulting CDB

## Case handling (schema-driven ingest)

Only `cui` and `name` are mandatory; the remaining columns are optional metadata resolved per concept. Example CSVs (`examples/cdb.csv`, `examples/cdb_2.csv`, `examples/complex_cdb.csv`) document the expected schema, and `examples/README.md` describes each column. Serialization defaults to `dill`-based pickling, controllable via the `cdb_format` parameter used when the CDB is later packaged into a model pack (US 18).

## Later stages (deferred)

- **Validation reporting.** Row-level diagnostics could be richer (line numbers, offending values) to speed up fixing large source files.
- **Schema versioning.** The CSV column set is conventional rather than versioned; a declared schema version would ease migration as new fields are added.
