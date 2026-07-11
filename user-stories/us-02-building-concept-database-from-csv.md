# US 02 Building a Concept Database from a CSV

This specification describes how a user turns a flat list of concepts into the Concept Database (CDB) that MedCAT's NER+L pipeline requires to recognise and link entities.

## Core Purpose

`CDBMaker.prepare_csvs` (`medcat/cdb_maker.py`) ingests one or more CSV files where each row provides a `cui` and a `name`, optionally alongside `ontologies`, `name_status`, `type_ids`, and `description`. A concept with multiple synonyms appears as multiple rows sharing the same `cui`, and the maker merges them into a single `CDB` entry with all known names attached.

## Key Design Consideration

`name_status` governs how aggressively a name is trusted at link time: `P` marks a preferred name that should resolve to this concept in the large majority of occurrences, `N` forces the name to always go through disambiguation, and `A` lets MedCAT decide automatically from training data. Getting this field wrong for a handful of rows has little impact, so the format tolerates it being omitted or approximate rather than requiring it to be exhaustively correct up front.

## Acceptance Criteria Summary

The specification requires:
- Multiple rows sharing a `cui` are merged into one concept with all names retained
- Only `cui` and `name` are mandatory; all other fields are optional and may appear on just one row per concept to reduce file size
- The resulting CDB can be persisted with `CDB.save` and reloaded with `CDB.load` without loss of names, ontology tags, or type IDs
- Malformed or duplicate rows are reported rather than silently corrupting the resulting CDB

## Implementation Notes

Example CSVs (`examples/cdb.csv`, `examples/cdb_2.csv`, `examples/complex_cdb.csv`) document the expected schema, and `examples/README.md` describes each column in detail. Serialization defaults to `dill`-based pickling, controllable via the `cdb_format` parameter used elsewhere when the CDB is packaged into a model pack.
