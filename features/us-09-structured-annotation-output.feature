# Executable counterpart of user-stories/us-09-structured-annotation-output.md
# Tagged @wip: scenarios are skipped until the steps in
# steps/annotation_output_steps.py are implemented (see features/README.md).
@wip @us-09
Feature: Getting Structured Annotation Output for a Document
  As a developer integrating MedCAT into a pipeline
  I want to get a document's annotations as a plain dictionary or JSON
  So that I can store, index, or ship them without holding a spaCy Doc in memory

  Scenario: Each entity carries the full structured field set
    Given a document with linked entities
    When get_entities runs
    Then each entity yields cui, pretty_name, source_value, detected_name, start, end, type_ids, types, acc, context_similarity, id, and a meta_anns field

  Scenario: Requested cross-ontology maps are attached
    Given the addl_info keys "cui2icd10" and "cui2snomed" are requested
    When annotation runs
    Then each requested map is attached under the key after the "2", or is empty when the CDB was built without full_build

  Scenario: only_cui collapses the output to bare identifiers
    Given only_cui is set to true
    When output is built
    Then each entity collapses to its id mapped to a cui and everything else is dropped

  Scenario: A direct link reports acc of 1 without measuring similarity
    Given a directly-linked entity with a single unambiguous candidate
    When output is built
    Then acc is 1 and no similarity was actually computed

  Scenario: A failed batch member yields empty output rather than an exception
    Given a None document from a failed batch member
    When output is built
    Then an empty entities-and-tokens structure is emitted instead of raising
