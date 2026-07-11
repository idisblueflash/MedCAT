# US 03 Unsupervised Training for Context Vectors and Spell Checking

This specification describes how MedCAT improves its linking accuracy and spelling normalisation purely from unlabelled text, without requiring any human-annotated examples.

## Core Purpose

`CAT.train(data_iterator)` (`medcat/cat.py:620`) streams raw documents through the pipeline, and for every detected name it updates that CUI's running context vector and the vocabulary's word-frequency counts. Over enough documents, the concept's context vector converges toward the language actually surrounding it in the target corpus, and the vocabulary accumulates frequency statistics used for spell-check suggestions.

## Key Design Consideration

Because this process has no ground truth to check against, it relies entirely on volume and frequency: a name seen consistently in a similar context builds a reliable vector, while a rare or noisy occurrence contributes little and is naturally down-weighted rather than treated as authoritative. This self-supervised step is explicitly the precursor to, not a replacement for, supervised correction (see US 04).

## Acceptance Criteria Summary

The specification requires:
- Running `cat.train` over a corpus updates context vectors without requiring any annotation input
- Word frequency counts accumulated during training feed the spell-checker used during preprocessing
- The unigram table size used for negative sampling is configurable (`unigram_table_size`, default `100000000`) so small test corpora aren't forced to allocate a table sized for production-scale vocabularies
- Training can run repeatedly over additional data without discarding previously learned vectors

## Implementation Notes

Vocabulary construction and word-frequency accumulation live in `medcat/utils/make_vocab.py` and `medcat/vocab.py`; the `Vocab` object produced here is the same one consumed by `medcat/preprocessing/normalizers.py` for spell-check suggestions during subsequent annotation.
