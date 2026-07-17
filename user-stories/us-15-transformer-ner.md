# US 15 Recognising Entities with a Transformer NER Model

As a *model builder whose entities can't just be looked up in a dictionary*, I want to *use a trained transformer model to recognise spans of text*, so that *I can detect things with no fixed spelling — names, dates, hospital numbers — that the dictionary-based matcher (US 05) simply cannot find, because it only knows what's already written in the CDB*.

("Transformer" here means a type of neural network, the same family of model behind tools like BERT.)

The dictionary matcher can only find what's already listed in the CDB. That's fine for standard medical concepts, but hopeless for "open" categories like names or ID numbers, which have no fixed list. `TransformersNER` (`medcat/ner/transformers_ner.py:36`) is the alternative: a HuggingFace token-classification model that predicts spans directly from the raw text. It's wrapped so it plugs into the same spaCy pipeline, writing to the same `doc._.ents` with the same `_.cui` and `_.confidence` fields as everything else. You add it with `CAT(addl_ner=...)`.

Remember from US 03 that the dictionary matcher and linker are only added *if a vocab exists*. So if you pass `addl_ner` but no vocab, you get a pipeline that is purely the transformer — no dictionary matching at all. If you pass both, they work side by side, and US 07's "longest match wins" rule decides between them wherever their outputs overlap.

Here's something to watch out for: this transformer still has to speak in CUIs (concept codes) — its output labels are a fixed set of CDB concepts. `expand_model_with_concepts(cui2preferred_name)` (`medcat/ner/transformers_ner.py:362`) lets you grow that label set to include new concepts. By default (`use_avg_init=True`), each new label starts out as the *average* of all the existing labels. This is a sensible way to "warm start" a new concept, but it's also silent: a newly added concept starts life predicting something close to the average of everything the model already knew, until it gets properly trained. Nothing in the output tells you whether a label is well-trained or freshly grafted on.

## Acceptance Criteria

1. Given a `TransformersNER` is passed in as `addl_ner`
   - when a document is processed
     - then predicted spans are written to `doc._.ents` with a real `cui` and a real `confidence` score — unlike the dictionary matcher, which always sets confidence to `-1`
2. Given a `CAT` is built with `addl_ner` but no vocab
   - when the pipeline is built
     - then neither the dictionary matcher nor the context linker gets added — the transformer becomes the entire recognition pipeline
3. Given both a vocab and an `addl_ner` are present
   - when a document is processed
     - then both recognisers contribute entities, and US 07's longest-span rule decides which ones survive where they overlap
4. Given `expand_model_with_concepts(cui2preferred_name)` is called
   - when it runs
     - then the model's label set grows to include the new concepts, with new labels starting at the average of the existing ones (when `use_avg_init=True`)
5. Given multiprocessing is attempted on a GPU build of torch
   - when a shared-memory error occurs
     - then that low-level `RuntimeError` is caught and re-raised as a clearer `ValueError`, telling you to save and reload the model from disk, or install a CPU-only version of torch (see US 17)
6. Given training data has labels that aren't in the model's label set, and `ignore_extra_labels=True`
   - when training runs
     - then those annotations are simply skipped, instead of causing a failure

## Case handling (a teammate, not a replacement)

`TransformersNER` is deliberately built as one more piece of the pipeline, not a separate fork of the whole system. It produces the exact same entity structure as everything else, so MetaCAT (US 13), RelCAT (US 14), the output format (US 09), and evaluation (US 19) all keep working without any changes. The cost of fitting in this way is that its predictions must be expressed as CUIs, which is why the label-expansion tool above exists. Tests for this live in `tests/ner/test_transformers_ner.py` and `tests/test_transformers_ner.py`.

## Later stages (deferred)

- **No record of which recogniser found an entity.** The output doesn't say whether an entity came from the dictionary matcher or from the transformer, which makes debugging a mixed pipeline harder than it needs to be.
- **Freshly-grafted labels look the same as trained ones.** `use_avg_init` gives plausible-looking confidence scores even for concepts the model has never actually been trained on.
