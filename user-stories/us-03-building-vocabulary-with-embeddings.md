# US 03 Building a Vocabulary with Word Embeddings

As a *model builder*, I want to *build a vocabulary of words, word counts, and embedding vectors from a text corpus*, so that *the linker can turn the words around a mention into a vector, and the spell-checker knows what a real word looks like*.

An "embedding vector" is just a list of numbers that represents a word's meaning, so that similar words end up with similar numbers.

`MakeVocab` (`medcat/utils/make_vocab.py:15`) reads a large body of text (a "corpus") and counts every word with its `make` method (`:64`; it can also mix in the CDB's own concept names with `join_cdb=True`). Then `add_vectors` (`:123`) attaches an embedding vector to each word. The result is a `Vocab` object (`medcat/vocab.py`), which also keeps a table of word frequencies (`make_unigram_table`, `:179`). Training later draws random "negative" words from that table via `get_negative_samples` (`:216`) — see US 10.

Here's the key idea: the CDB (US 01) only knows concept *names*. It knows nothing about ordinary *language*. The `Vocab` is what supplies that missing knowledge.

This dependency matters more than it looks, and it's easy to miss. Disambiguation (US 06) works by averaging the embedding vectors of the words around a mention, then comparing that average to a vector learned for each concept. Without a `Vocab`, there is no context vector and no comparison — in fact `CAT._create_pipeline` silently builds a pipeline with **no dictionary matcher and no linker at all**, because both are only added `if self.vocab is not None`.

There's also a hidden failure mode. A word that's missing from the vocabulary doesn't count as "zero" in the context vector — it's simply skipped, without any warning. So if every word around a mention happens to be missing from the vocabulary, the context vector ends up empty and the mention can't be linked at all. From the outside this looks like the recogniser missed something; really, it's a gap in the vocabulary.

## Acceptance Criteria

1. Given a corpus to read
   - when `make` builds the vocabulary
     - then every word gets a count, and `remove_words_below_cnt(n)` (`medcat/vocab.py:55`) can drop rare words — dropping a word also removes its vector
2. Given `add_vectors` is run with a source of embeddings
   - when it finishes
     - then every known word gets a vector; words that were only counted (no vector) still help spell-checking, but add nothing to context vectors
3. Given a word seen while annotating a document that isn't in the vocabulary
   - when the context vector is averaged
     - then that word is skipped completely — it does not add a zero, it adds nothing at all
4. Given a mention where every surrounding word is missing from the vocabulary
   - when linking runs
     - then there is no context vector, so nothing can be compared, and the mention effectively cannot be linked
5. Given training asks for negative samples
   - when `get_negative_samples` runs
     - then it picks words from the frequency-weighted table, optionally skipping punctuation and numbers

## Case handling (three situations for any given word)

A word can be: in the vocabulary with a vector (helps with context), in the vocabulary without a vector (helps with spell-checking only), or missing entirely (helps with nothing). Only the first two are handled on purpose — the third one fails silently, which is exactly why it's worth checking your vocabulary's coverage before assuming the linker itself is broken. Tests for this live in `tests/test_vocab.py`.

## Later stages (deferred)

- **No coverage report.** Nothing currently measures what fraction of a corpus's words actually got a vector — probably the single best early warning sign for linking quality — so a vocabulary gap is hard to spot ahead of time.
- **Vocab and CDB can drift apart.** `join_cdb=True` only mixes CDB names into the vocabulary at build time. Concepts added later (US 12) are not reflected, and the vocabulary quietly falls behind the CDB.
