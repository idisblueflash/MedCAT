# US 01 Building a Concept Database from a CSV

As a *knowledge engineer*, I want to *turn a simple list of medical concepts into a Concept Database (CDB)*, so that *MedCAT can find and link the concepts I care about inside text*.

A Concept Database (CDB) is a lookup table. It tells MedCAT which words in a document point to which medical concept.

You give MedCAT this list as one or more CSV files (a CSV is a spreadsheet saved as plain text). Each row needs two things: a `cui` (a unique code number for the concept) and a `name` (a word or phrase people actually use for it). You can also add extra columns if you have them: `ontologies` (which vocabulary the concept comes from), `name_status`, `type_ids`, and `description`.

Many concepts have more than one name — these are called synonyms. If a concept has several names, just add several rows that share the same `cui`. The tool that reads the CSV, `CDBMaker.prepare_csvs` (in `medcat/cdb_maker.py`), joins those rows together into one entry in the CDB, keeping every name.

One column deserves extra care: `name_status`. It tells MedCAT how much to trust a name:
- `P` (preferred) — this name almost always means this concept.
- `N` (not preferred) — the name is ambiguous, so MedCAT should think harder before deciding what it means.
- `A` (automatic) — let MedCAT decide later, from training data.

Don't worry about getting `name_status` perfect on every row. A few mistakes here have little effect, so it's fine to leave it out or guess.

## Acceptance Criteria

1. Given several CSV rows that share the same `cui`
   - when `prepare_csvs` builds the CDB
     - then all those rows are merged into one concept, keeping every name
2. Given a CSV that only fills in the `cui` and `name` columns
   - when the CDB is built
     - then it still works — every other column is optional, so files can stay small
3. Given a CDB that has already been built
   - when it is saved with `CDB.save` and loaded again with `CDB.load`
     - then the names, ontology tags, and type IDs come back exactly as they were
4. Given a CSV with broken or duplicate rows
   - when the file is read
     - then MedCAT reports the problem rows instead of quietly building a broken CDB

## Case handling (which columns you need)

Only `cui` and `name` are required. Everything else is optional information MedCAT can fill in per concept. Look at the example CSV files (`examples/cdb.csv`, `examples/cdb_2.csv`, `examples/complex_cdb.csv`) to see the expected columns, and read `examples/README.md` for what each column means. By default MedCAT saves the CDB using a Python tool called `dill` (a more powerful version of `pickle`); you can change this with the `cdb_format` setting, which also matters later when everything is packaged into a model pack (US 18).

## Later stages (deferred)

- **Better error messages.** The tool could say more about exactly which row and value caused a problem, to help fix large files faster.
- **A versioned schema.** The set of CSV columns is a convention, not a strict version number. A declared schema version would make it easier to update the format later without breaking old files.
