# US 09 Large-Scale Multiprocessing Annotation of EHR Corpora

As a *data engineer*, I want to *annotate very large document corpora in parallel*, so that *I can scale from a handful of notes to 100M+ documents without exhausting memory*.

`CAT.multiprocessing_batch_char_size` and `CAT.multiprocessing_batch_docs_size` (`medcat/cat.py:1304,1558`) parallelise `get_entities` across multiple worker processes, batching the input either by total character count or by document count, depending on which better fits the shape of the corpus.

The choice exists because a fixed document-count batch can overload memory when document lengths vary wildly (short triage notes mixed with multi-page discharge summaries), while a fixed character-size batch keeps per-worker memory pressure predictable regardless of length variance — at the cost of batches holding uneven numbers of documents.

## Acceptance Criteria

1. Given a configured number of worker processes
   - when annotation runs over a large corpus
     - then throughput scales with the worker count without unbounded memory growth
2. Given a single malformed or unusually large document
   - when it is encountered mid-corpus
     - then it does not halt processing of the rest of the corpus
3. Given a corpus of a particular shape
   - when a batching strategy is chosen
     - then both character-size and document-count strategies are available and independently configurable
4. Given the project's stated scale target
   - when the approach is validated
     - then it holds at the 100M+ documents described in the release notes

## Case handling (batch-by-size vs batch-by-count)

Input is partitioned into batches by the selected strategy, dispatched to workers, and results streamed back; a failing document is isolated rather than fatal. Multiprocessing builds on spaCy's parallel `nlp.pipe`, orchestrated through `medcat/pipeline/pipe_runner.py`. Coverage lives in `tests/test_pipe.py` and `tests/test_pipe_runner.py`.

## Later stages (deferred)

- **Adaptive batching.** The batch strategy and size are chosen up front; adapting them from observed per-worker memory would remove manual tuning.
- **Distributed execution.** Parallelism is within a single machine's processes; a multi-node backend would extend the same API to cluster scale.
