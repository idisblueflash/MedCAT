# Executable counterpart of user-stories/us-01-ner-plus-linking-to-ontologies.md
# Tagged @wip: scenarios are skipped until the steps in
# steps/ner_linking_steps.py are implemented (see features/README.md).
@wip @us-01
Feature: Named Entity Recognition and Linking to Clinical Ontologies
  As a clinical NLP engineer
  I want to extract concept mentions from free-text notes and link each to a stable ontology identifier
  So that downstream analytics run on coded concepts instead of raw strings

  Scenario: Annotating a document returns coded entities
    Given a clinical document
    When get_entities runs the pipeline
    Then each detected entity is returned with its CUI, character offsets, and source name

  Scenario: Ambiguous names are disambiguated by context
    Given a name that maps to multiple CUIs
    When the linker scores the candidates against the surrounding context
    Then the CUI whose learned context vector best matches is chosen, only above the similarity threshold

  Scenario: Cross-ontology references are attached on request
    Given the addl_info keys "cui2icd10" and "cui2snomed" are requested
    When annotation runs
    Then each result additionally carries the requested cross-ontology references

  Scenario: Only-CUI mode returns bare identifiers
    Given only_cui is set to true
    When annotation runs
    Then the output is restricted to bare CUIs

  Scenario: Batch annotation preserves input order
    Given a batch of documents
    When get_entities_multi_texts runs
    Then results are returned in the same order as the input documents
