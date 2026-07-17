# US 17 Large-Scale Multiprocessing Annotation of EHR Corpora

As a *data engineer*, I want to *annotate a very large collection of documents in parallel*, so that *I can scale from a handful of notes to more than 100 million documents without running out of memory*.

`CAT.multiprocessing_batch_char_size` and `CAT.multiprocessing_batch_docs_size` (`medcat/cat.py:1304,1558`) run `get_entities` across several worker processes at the same time. Documents are split into batches either by total character count, or by number of documents, whichever fits your data better.

Why two options? If document lengths vary a lot — short triage notes mixed with long, multi-page discharge summaries — a batch based on a fixed *number* of documents can overload memory, because some batches will contain much more text than others. A batch based on a fixed *character count* keeps memory use predictable no matter how much lengths vary — the trade-off is that each batch then contains an uneven number of documents.

## Acceptance Criteria

1. Given a chosen number of worker processes
   - when annotation runs over a large corpus
     - then speed increases as more workers are added, without memory use growing without limit
2. Given a single broken or unusually large document appears in the middle of the corpus
   - when it is processed
     - then it does not stop the rest of the corpus from being processed
3. Given a corpus with a particular shape (document lengths)
   - when choosing how to batch it
     - then both strategies — by character count and by document count — are available, and can be set independently
4. Given the project's stated goal of handling very large corpora
   - when the approach is tested at scale
     - then it holds up at the 100-million-plus document scale mentioned in the release notes

## Case handling (splitting work by size or by count)

The input is split into batches using whichever strategy was chosen, sent out to the worker processes, and results are streamed back as they finish. A document that fails doesn't bring down the whole run — it's handled on its own. This multiprocessing is built on top of spaCy's own parallel processing (`nlp.pipe`), coordinated through `medcat/pipeline/pipe_runner.py`. Tests live in `tests/test_pipe.py` and `tests/test_pipe_runner.py`.

## Later stages (deferred)

- **No automatic batch tuning.** The batching strategy and size are chosen ahead of time by the user. Adjusting them automatically based on observed memory use per worker would remove the need for manual tuning.
- **No support for running across multiple machines.** Parallelism currently happens only within a single machine's processes. Extending this to run across a cluster of machines would allow even larger scale.
