# US 10 Unsupervised Training for Context Vectors and Spell Checking

As an *NLP engineer*, I want to *refine concept context vectors and vocabulary statistics from unlabelled text*, so that *linking accuracy and spell-checking improve on my target corpus without any manual annotation*.

`CAT.train(data_iterator)` (`medcat/cat.py:620`) streams raw documents through the pipeline, and for every detected name it updates that CUI's running context vector and the vocabulary's word-frequency counts. Over enough documents, a concept's context vector converges toward the language actually surrounding it in the corpus, and the vocabulary accumulates the frequency statistics used for spell-check suggestions.

Because there is no ground truth to check against, the process relies entirely on volume and frequency: a name seen consistently in a similar context builds a reliable vector, while a rare or noisy occurrence contributes little and is naturally down-weighted rather than treated as authoritative. This self-supervised step is explicitly the precursor to — not a replacement for — supervised correction (US 11).

## Acceptance Criteria

1. Given a corpus of unlabelled documents
   - when `cat.train` runs over it
     - then context vectors are updated with no annotation input required
2. Given training has processed documents
   - when preprocessing later runs the spell-checker
     - then it draws on the word-frequency counts accumulated during training
3. Given a small test corpus
   - when `unigram_table_size` (default `100000000`) is lowered
     - then negative sampling uses a smaller table instead of forcing a production-scale allocation
4. Given a model already trained on some data
   - when `cat.train` runs again on additional data
     - then previously learned vectors are retained rather than discarded

## Case handling (frequency-driven updates)

Each detected name contributes a context-vector update and a vocabulary count; nothing is treated as authoritative from a single occurrence. Vocabulary construction and word-frequency accumulation live in `medcat/utils/make_vocab.py` and `medcat/vocab.py`; the `Vocab` produced here is the same one consumed by `medcat/preprocessing/normalizers.py` for spell-check suggestions during subsequent annotation.

## Later stages (deferred)

- **Convergence signals.** Training exposes no built-in "vectors have stabilised" metric; a convergence/early-stop indicator would help size corpora.
- **Noise down-weighting.** Rare-context handling is implicit in the frequency model; an explicit outlier filter could further reduce noisy updates.
