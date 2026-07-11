# US 03 Building a Vocabulary with Word Embeddings

As a *model builder*, I want to *build a vocabulary of words, counts, and embedding vectors from a text corpus*, so that *the linker can represent the context around a mention as a vector and the spell-checker knows what a real word looks like*.

`MakeVocab` (`medcat/utils/make_vocab.py:15`) scans a corpus, counts every token via `make` (`:64`, optionally folding in the CDB's own name tokens with `join_cdb=True`), and then `add_vectors` (`:123`) attaches an embedding vector per word. The resulting `Vocab` (`medcat/vocab.py`) also maintains a frequency-weighted unigram table (`make_unigram_table`, `:179`) from which `get_negative_samples` (`:216`) draws during training (US 10). The CDB (US 01) knows names; it knows nothing about *language* — the `Vocab` is what supplies it.

The dependency is load-bearing and easy to miss: disambiguation (US 06) averages the embedding vectors of the words surrounding a mention and compares that to a per-concept learned vector, so without a `Vocab` there is no context, no similarity, and `CAT._create_pipeline` silently builds a pipeline with **no dictionary NER and no linker at all** (both are added only `if self.vocab is not None`). The failure is asymmetric, too: a word absent from the vocab contributes *nothing* to the context vector — it is skipped, not zeroed, not flagged — so a mention surrounded entirely by out-of-vocabulary words gets an empty context vector and becomes effectively unlinkable. It looks like a recall problem in the recogniser; it is actually a vocabulary hole.

## Acceptance Criteria

1. Given a corpus iterator
   - when `make` builds the vocab
     - then every token receives a count, and `remove_words_below_cnt(n)` (`medcat/vocab.py:55`) can prune the long tail — pruning also drops that word's vector
2. Given `add_vectors` with an embedding source
   - when it runs
     - then each known word gains a vector, while words counted without a vector still serve spell-checking but contribute nothing to context vectors
3. Given a token encountered at annotation time that is not in the vocab
   - when the context vector is averaged
     - then it is skipped entirely — it does not contribute a zero vector, it contributes nothing
4. Given a mention where every surrounding token is out-of-vocabulary
   - when linking runs
     - then the context vector is absent, similarity cannot be scored, and the candidate is effectively unlinkable
5. Given negative sampling is requested during training
   - when `get_negative_samples` runs
     - then it draws from the frequency-weighted unigram table, optionally ignoring punctuation and numbers

## Case handling (present / present-without-vector / absent)

A word is in the vocab with a vector (contributes to context), in the vocab without one (contributes to spell-check only), or absent (contributes nothing). Only the first two are handled explicitly; the third degrades silently, which is exactly why vocabulary coverage has to be verified before blaming the linker. Coverage lives in `tests/test_vocab.py`.

## Later stages (deferred)

- **No coverage report.** Nothing measures what fraction of a corpus's tokens actually resolved to a vector — arguably the single best predictor of linking quality — so a vocabulary hole cannot be quantified up front.
- **Vocab and CDB drift.** `join_cdb=True` folds CDB name-tokens into the vocab at build time; concepts added later (US 12) are not reflected, and the vocab silently falls behind the CDB.
