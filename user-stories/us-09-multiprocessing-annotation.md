# US 09 Large-Scale Multiprocessing Annotation of EHR Corpora

This specification describes how MedCAT scales entity annotation from a handful of documents to corpora of 100M+ documents without exhausting available memory.

## Core Purpose

`CAT.multiprocessing_batch_char_size` and `CAT.multiprocessing_batch_docs_size` (`medcat/cat.py:1304,1558`) parallelise `get_entities` across multiple worker processes, batching the input either by total character count or by document count depending on which better fits the shape of the corpus.

## Key Design Consideration

The choice between batching by character size versus document count exists because a fixed document-count batch can badly overload memory when documents vary wildly in length (a mix of short triage notes and multi-page discharge summaries), while a fixed character-size batch keeps per-worker memory pressure predictable regardless of document-length variance, at the cost of batches containing uneven numbers of documents.

## Acceptance Criteria Summary

The specification requires:
- Throughput scales with the configured number of worker processes without unbounded memory growth
- A single malformed or unusually large document does not halt processing of the rest of the corpus
- Both batching strategies (character-size and document-count) are available and independently configurable
- The approach is validated at the scale described in the project's release notes (100M+ documents)

## Implementation Notes

Multiprocessing builds on spaCy's parallel `nlp.pipe` execution, orchestrated through `medcat/pipeline/pipe_runner.py`. Coverage lives in `tests/test_pipe.py` and `tests/test_pipe_runner.py`.
