# US 15 Recognising Entities with a Transformer NER Model

As a *model builder whose entities are not dictionary-matchable*, I want to *use a trained transformer to recognise spans*, so that *I can detect things with no fixed surface form — names, dates, hospital numbers — that the vocab-based matcher (US 05) structurally cannot find*.

The dictionary NER can only find what is in the CDB: fine for ontology concepts, hopeless for open classes. `TransformersNER` (`medcat/ner/transformers_ner.py:36`) is the alternative recogniser — a HuggingFace token-classification model that predicts spans directly from text, wrapped so it plugs into the same spaCy pipeline and writes the same `doc._.ents` with the same `_.cui` and `_.confidence` fields. It is added via `CAT(addl_ner=...)`. Because `_create_pipeline` adds the vocab-based NER and linker only *if a vocab exists*, passing `addl_ner` with no vocab yields a pure transformer pipeline with no dictionary matching at all; passing both makes them coexist, with US 07's overlap arbitration deciding between their outputs.

The risk is that this component still speaks CUIs. Its label set is a set of CDB concepts, and `expand_model_with_concepts(cui2preferred_name)` (`medcat/ner/transformers_ner.py:362`) grows the classification head to cover new ones — initialising the new rows, by default (`use_avg_init=True`), to the *average* of the existing ones. That is a sensible warm start and a silent one: a newly-added concept begins life predicting something close to the mean of everything the model already knew, and does so until it is trained. Nothing in the output distinguishes a well-trained label from a freshly-grafted one.

## Acceptance Criteria

1. Given a `TransformersNER` passed as `addl_ner`
   - when a document is processed
     - then predicted spans are written to `doc._.ents` with a `cui` and a real `confidence` — unlike the vocab NER, which sets confidence to `-1`
2. Given a `CAT` constructed with `addl_ner` but no vocab
   - when the pipeline is built
     - then no vocab-based NER and no context linker are added: the transformer is the entire recognition pipeline
3. Given both a vocab and an `addl_ner`
   - when a document is processed
     - then both recognisers contribute entities, and US 07's longest-span arbitration decides which survive where they overlap
4. Given `expand_model_with_concepts(cui2preferred_name)`
   - when it runs
     - then the classification head grows to cover the new CUIs, with new rows initialised to the mean of existing rows when `use_avg_init=True`
5. Given multiprocessing is attempted with a torch-GPU build
   - when a share-memory error is raised
     - then the `RuntimeError` (`_share_filename_: only available on CPU`) is caught and re-raised as a `ValueError` telling the user to round-trip the model through disk or install CPU-only torch (see US 17)
6. Given training data with labels not in the model's label set and `ignore_extra_labels=True`
   - when training runs
     - then those annotations are dropped rather than causing a failure

## Case handling (a peer recogniser, not a replacement)

`TransformersNER` is deliberately a *component*, not a fork of the system. It produces the same entity structure, so MetaCAT (US 13), RelCAT (US 14), output (US 09), and evaluation (US 19) all work unchanged. The cost of that uniformity is that it must express its predictions as CUIs, which forces the head-expansion machinery above. Coverage lives in `tests/ner/test_transformers_ner.py` and `tests/test_transformers_ner.py`.

## Later stages (deferred)

- **No provenance on entities.** Nothing on the output entity says whether it came from the dictionary matcher or the transformer, which makes debugging a mixed pipeline unnecessarily hard.
- **Grafted labels are indistinguishable from trained ones.** `use_avg_init` produces plausible-looking confidences for concepts the model has never seen.
