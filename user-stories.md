# MedCAT User Stories

This index catalogs feature specifications ("user stories") describing MedCAT's core capabilities, derived from the codebase under `medcat/`. Each entry links to a detailed specification under [`user-stories/`](user-stories/), following the format established in [paper-degist's user-stories](https://github.com/idisblueflash/paper-degist/blob/master/user-stories/us-10-resolving-doi-from-title.md).

| # | Title | Description |
| --- | --- | --- |
| [US 01](user-stories/us-01-ner-plus-linking-to-ontologies.md) | Named Entity Recognition and Linking to Clinical Ontologies | Extract concept mentions from free text and link them to UMLS/SNOMED-CT via context-aware disambiguation. |
| [US 02](user-stories/us-02-building-concept-database-from-csv.md) | Building a Concept Database from a CSV | Turn a flat list of concepts (CUI, name, synonyms) into a Concept Database usable by the NER+L pipeline. |
| [US 03](user-stories/us-03-unsupervised-training.md) | Unsupervised Training for Context Vectors and Spell Checking | Refine concept context vectors and vocabulary frequency statistics from unlabelled text. |
| [US 04](user-stories/us-04-supervised-training.md) | Supervised Fine-Tuning from Annotated Trainer Exports | Correct linking mistakes using human-reviewed MedCATtrainer annotation exports. |
| [US 05](user-stories/us-05-meta-annotation-classification.md) | Meta-Annotation Classification with MetaCAT | Classify contextual attributes (negation, experiencer, temporality) on top of already-linked spans. |
| [US 06](user-stories/us-06-relation-extraction.md) | Relation Extraction Between Linked Concepts | Predict relationships between pairs of linked concepts using RelCAT. |
| [US 07](user-stories/us-07-deidentification.md) | De-Identification of Clinical Text | Detect and redact PII/PHI in clinical text via the DeIdModel wrapper. |
| [US 08](user-stories/us-08-model-pack-packaging.md) | Packaging and Loading Portable Model Packs | Bundle CDB, Vocab, config, and attached models into a single deployable model pack archive. |
| [US 09](user-stories/us-09-multiprocessing-annotation.md) | Large-Scale Multiprocessing Annotation of EHR Corpora | Parallelize entity annotation across processes for corpora of 100M+ documents. |
| [US 10](user-stories/us-10-regression-testing.md) | Regression Testing Across Model and Ontology Versions | Validate a new model pack against expected concept detections using a placeholder-based regression suite. |
| [US 11](user-stories/us-11-incremental-model-correction.md) | Incrementally Correcting a Live Model | Apply targeted fixes (add/unlink names, group CUIs) to a running model without full retraining. |
| [US 12](user-stories/us-12-building-from-raw-ontology-releases.md) | Building CDB and Vocab from Raw UMLS/SNOMED-CT Releases | Convert official UMLS/SNOMED-CT release files into a usable CDB and Vocab end-to-end. |
| [US 13](user-stories/us-13-model-evaluation-kfold.md) | Model Evaluation via K-Fold Cross-Validation | Measure per-concept precision/recall/F1 quality across folds of a MedCATtrainer export. |
| [US 14](user-stories/us-14-usage-monitoring.md) | Opt-In Usage Monitoring | Locally log pipeline invocation events per model version, entirely disk-based and off by default. |
