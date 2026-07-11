# MedCAT User Stories

This index catalogs feature specifications ("user stories") describing MedCAT's core capabilities, derived from the codebase under `medcat/`. Each entry links to a detailed specification under [`user-stories/`](user-stories/), following the format established in [paper-degist's user-stories](https://github.com/idisblueflash/paper-degist/blob/master/user-stories/us-10-resolving-doi-from-title.md).

Stories are grouped by the stage of work they belong to — **build a model → annotate a document → train → layer on top → operate** — and, within the annotation group, ordered to follow the pipeline as it actually runs.

## The one-paragraph version

MedCAT extracts medical concepts from free clinical text and links them to an ontology (SNOMED-CT, UMLS). The core architectural insight is that **recognition and decision are separated**. A greedy dictionary matcher (US 05) deliberately *over-produces* candidate spans, each carrying every concept its name could mean; a context model (US 06) then decides which one it is, by comparing the words around the mention to a vector learned per concept. Everything else in the system exists to feed, correct, or wrap those two steps.

## Building a model

| # | Title | Description |
| --- | --- | --- |
| [US 01](user-stories/us-01-building-concept-database-from-csv.md) | Building a Concept Database from a CSV | Turn a flat list of concepts (CUI, name, synonyms) into a Concept Database usable by the NER+L pipeline. |
| [US 02](user-stories/us-02-building-from-raw-ontology-releases.md) | Building CDB and Vocab from Raw UMLS/SNOMED-CT Releases | Convert official UMLS/SNOMED-CT release files into a usable CDB and Vocab end-to-end. |
| [US 03](user-stories/us-03-building-vocabulary-with-embeddings.md) | Building a Vocabulary with Word Embeddings | Build word counts, embedding vectors, and the unigram table the linker and spell-checker depend on. |

## Annotating a document (the pipeline, in order)

| # | Title | Description |
| --- | --- | --- |
| [US 04](user-stories/us-04-normalising-and-spell-correcting-tokens.md) | Normalising and Spell-Correcting Tokens | Skip, lemma-normalise, and optionally spell-correct tokens into the CDB's stored form before matching. |
| [US 05](user-stories/us-05-detecting-candidate-concept-mentions.md) | Detecting Candidate Concept Mentions in Text | Greedy dictionary prefix-walk that over-produces every span a name could match, deciding nothing. |
| [US 06](user-stories/us-06-disambiguating-a-mention-by-context.md) | Disambiguating an Ambiguous Mention Using Its Context | Pick one candidate CUI (or none) by comparing surrounding words to each concept's learned context vector. |
| [US 07](user-stories/us-07-resolving-overlapping-detections.md) | Resolving Overlapping Detections into One Annotation Set | Arbitrate nested/overlapping spans, longest-match-wins, into a single non-overlapping set. |
| [US 08](user-stories/us-08-restricting-linking-to-concept-subset.md) | Restricting Linking to a Subset of Concepts | Constrain output to an allow-/deny-list of CUIs without retraining or manual post-filtering. |
| [US 09](user-stories/us-09-structured-annotation-output.md) | Getting Structured Annotation Output for a Document | Return annotations as a plain dict/JSON, including the `source_value`/`detected_name` audit pair. |

## Training

| # | Title | Description |
| --- | --- | --- |
| [US 10](user-stories/us-10-unsupervised-training.md) | Unsupervised Training for Context Vectors and Spell Checking | Refine concept context vectors and vocabulary frequency statistics from unlabelled text. |
| [US 11](user-stories/us-11-supervised-training.md) | Supervised Fine-Tuning from Annotated Trainer Exports | Correct linking mistakes using human-reviewed MedCATtrainer annotation exports. |
| [US 12](user-stories/us-12-incremental-model-correction.md) | Incrementally Correcting a Live Model | Apply targeted fixes (add/unlink names, group CUIs) to a running model without full retraining. |

## Layers on top of the entities

| # | Title | Description |
| --- | --- | --- |
| [US 13](user-stories/us-13-meta-annotation-classification.md) | Meta-Annotation Classification with MetaCAT | Classify contextual attributes (negation, experiencer, temporality) on top of already-linked spans. |
| [US 14](user-stories/us-14-relation-extraction.md) | Relation Extraction Between Linked Concepts | Predict relationships between pairs of linked concepts using RelCAT. |
| [US 15](user-stories/us-15-transformer-ner.md) | Recognising Entities with a Transformer NER Model | Detect open-class spans (names, dates, IDs) with a transformer recogniser the dictionary matcher cannot find. |
| [US 16](user-stories/us-16-deidentification.md) | De-Identification of Clinical Text | Detect and redact PII/PHI in clinical text via the DeIdModel wrapper. |

## Operating a model

| # | Title | Description |
| --- | --- | --- |
| [US 17](user-stories/us-17-multiprocessing-annotation.md) | Large-Scale Multiprocessing Annotation of EHR Corpora | Parallelize entity annotation across processes for corpora of 100M+ documents. |
| [US 18](user-stories/us-18-model-pack-packaging.md) | Packaging and Loading Portable Model Packs | Bundle CDB, Vocab, config, and attached models into a single deployable model pack archive. |
| [US 19](user-stories/us-19-measuring-performance-against-gold-standard.md) | Measuring Performance Against a Gold Standard | Compute per-concept precision/recall/F1 with FP/FN example sentences from a MedCATtrainer export. |
| [US 20](user-stories/us-20-model-evaluation-kfold.md) | Model Evaluation via K-Fold Cross-Validation | Measure per-concept precision/recall/F1 quality across folds of a MedCATtrainer export. |
| [US 21](user-stories/us-21-regression-testing.md) | Regression Testing Across Model and Ontology Versions | Validate a new model pack against expected concept detections using a placeholder-based regression suite. |
| [US 22](user-stories/us-22-fitting-large-cdb-into-memory.md) | Fitting a Very Large Concept Database into Memory | Deduplicate a multi-million-concept CDB's keys via delegating dicts to fit it in RAM. |
| [US 23](user-stories/us-23-merging-concept-databases.md) | Merging Two Concept Databases | Combine two CDBs, count-weighting their learned context vectors, into one. |
| [US 24](user-stories/us-24-usage-monitoring.md) | Opt-In Usage Monitoring | Locally log pipeline invocation events per model version, entirely disk-based and off by default. |

## Four things worth knowing before you read

These cross-cutting behaviours surface repeatedly across the stories and are the most common source of confusion when debugging a model:

1. **An entity can vanish at three independent gates**, and the output format (US 09) does not say which one dropped it: below `similarity_threshold` (US 06), excluded by a filter (US 08), or beaten by a longer overlapping span (US 07). Debugging a missing annotation means checking all three.
2. **`name_status` in the source CSV is load-bearing.** A name marked `P` is used as a free training label during unsupervised training (US 10). Mark an ambiguous string `P` and the model silently learns the wrong context (US 01).
3. **No vocab means no linker.** `CAT._create_pipeline` only adds the dictionary NER and the context linker `if self.vocab is not None`. This is both a feature — it is how DeID works (US 16) — and a trap (US 03).
4. **The default supervised "test set" is the training set.** `test_size=0` makes `test_set = train_set = data` (US 12, US 19), so the F1 printed during training is a training-set F1.

## Note on the repository

MedCAT v1 has moved to [CogStack/cogstack-nlp](https://github.com/CogStack/cogstack-nlp), and a v2 exists at [CogStack/MedCAT2](https://github.com/CogStack/MedCAT2). These stories describe the `main` branch of the original repository as it stands.
