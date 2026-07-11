# Executable counterpart of user-stories/us-01-building-concept-database-from-csv.md
# Each Scenario is one acceptance criterion, driven against CDBMaker.prepare_csvs
# by the steps in steps/cdb_from_csv_steps.py.
@us-01
Feature: Building a Concept Database from a CSV
  As a knowledge engineer
  I want to turn a flat list of concepts into a Concept Database (CDB)
  So that MedCAT's NER+L pipeline can recognise and link the entities I care about

  Scenario: Rows sharing one CUI merge into a single concept
    Given a CSV where three rows share the CUI "S-195967001" with the names "Asthma", "Bronchial asthma", and "Reactive airway disease"
    When prepare_csvs builds the CDB
    Then the CDB holds one concept "S-195967001" whose names are "asthma", "bronchial~asthma", and "reactive~airway~disease"

  Scenario: A CUI and a name alone are enough
    Given a CSV that supplies only the CUI "S-73211009" and the name "Diabetes mellitus"
    When prepare_csvs builds the CDB
    Then the build succeeds and concept "S-73211009" has no type IDs

  Scenario: Names, ontology tags and type IDs survive a save/load round trip
    Given a full-build CSV concept "S-84114007" named "Heart failure" in ontology "SNOMED" with type IDs "T047|T190"
    When the CDB is saved and reloaded
    Then concept "S-84114007" keeps its names, the ontology tag "SNOMED", and the type IDs "T047" and "T190"

  Scenario Outline: Malformed rows are reported rather than silently added
    Given a CSV row whose CUI is "<cui>" and whose name is "<name>"
    When prepare_csvs builds the CDB
    Then a malformed-row warning is emitted and no concept is added

    Examples: rows missing a required field
      | cui        | name                 |
      |            | Orphan without a cui |
      | S-22298006 |                      |
      | S-49436004 | \| \|                |
