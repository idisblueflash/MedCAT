# US 10 Unsupervised Training for Context Vectors and Spell Checking

As an *NLP engineer*, I want to *improve concept context vectors and vocabulary statistics using plain, unlabelled text*, so that *linking accuracy and spell-checking get better for my own data, without anyone having to hand-annotate anything*.

"Unsupervised" here means: no one has told MedCAT the right answers — it just learns patterns from raw text on its own.

`CAT.train(data_iterator)` (`medcat/cat.py:620`) feeds plain documents through the pipeline one by one. Every time it detects a concept name, it updates two things: the running context vector for that concept (see US 06), and the word-frequency counts in the vocabulary (see US 03). After enough documents, a concept's context vector starts to reflect the actual language that tends to surround it in your data, and the vocabulary builds up the frequency statistics that spell-checking later relies on.

Since there's no "correct answer" to check against here, this process depends entirely on how often and how consistently something appears. A name that keeps showing up in similar surroundings ends up with a reliable vector; a name that appears rarely, or in unusual contexts, contributes very little and naturally carries less weight — it isn't treated as if it were certainly correct. This step is meant to come *before* supervised correction (US 11), not replace it.

## Acceptance Criteria

1. Given a corpus of documents with no labels
   - when `cat.train` runs over it
     - then context vectors get updated with no manual annotation needed at all
2. Given training has already processed some documents
   - when the spell-checker runs later during preprocessing
     - then it uses the word-frequency counts built up during that training
3. Given a small test corpus
   - when `unigram_table_size` (100,000,000 by default) is set lower
     - then negative sampling uses a smaller table instead of forcing a huge, production-scale one
4. Given a model that has already been trained on some data
   - when `cat.train` runs again on more data
     - then what it already learned is kept, not thrown away

## Case handling (learning by frequency, not by rule)

Every detected name adds one small update to its context vector and to the vocabulary's word count — no single occurrence is treated as definitely correct on its own. Building the vocabulary and counting word frequency happens in `medcat/utils/make_vocab.py` and `medcat/vocab.py`. The same `Vocab` object built here is later used by `medcat/preprocessing/normalizers.py` to suggest spelling corrections during annotation.

## Later stages (deferred)

- **No sign of "done learning."** Training doesn't currently tell you when the vectors have settled down and stopped changing much; a built-in signal for this would help decide how much data is enough.
- **No explicit noise filter.** Rare or unusual contexts are only down-weighted indirectly, through frequency. An explicit filter for outliers could reduce noisy updates further.
