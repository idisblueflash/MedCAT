# US 07 Resolving Overlapping Detections into One Annotation Set

As a *clinician analysing free-text notes*, I want to *get "diabetes mellitus type 2" as one annotation rather than three overlapping ones*, so that *each piece of text carries a single meaning and downstream counting does not double-count*.

Candidate detection over-produces by design: a greedy prefix walk emits every complete name it passes through, so nested and overlapping spans are normal, not exceptional. Disambiguation (US 06) then drops the ones that fail. What survives still overlaps, and `create_main_ann` (`medcat/utils/postprocessing.py:37`) is the arbiter. Its rule is entirely mechanical: sort the surviving entities by **text length, longest first**, then walk them, accepting an entity only if *none* of its tokens has already been claimed. Longest match wins; everything it covers is suppressed.

The risk is that "longest" is a proxy for "most specific", and the proxy is not always right. Length is measured in characters of surface text — not specificity, not confidence, not similarity — so a long, low-confidence match beats a short, high-confidence one it happens to overlap, and the context similarity computed at such cost in US 06 plays no part in this decision. The full, un-arbitrated set is not discarded (it stays on `doc._.ents`, and `general.show_nested_entities`, `medcat/config.py:378`, will surface it), but the default output is the arbitrated one.

## Acceptance Criteria

1. Given two surviving entities where one's span strictly contains the other's
   - when `create_main_ann` runs
     - then the longer one is kept and the shorter is suppressed from `doc.ents`
2. Given two entities that partially overlap by at least one token
   - when arbitration runs
     - then the longer text wins and the other is dropped entirely — not truncated, not merged
3. Given two overlapping entities of equal text length
   - when arbitration runs
     - then the one encountered first in sorted order wins; the tie-break is incidental, not principled
4. Given entities that do not overlap at all
   - when arbitration runs
     - then all are kept, in the order the sort produced
5. Given `general.show_nested_entities` is enabled
   - when output is built (US 09)
     - then it is drawn from `doc._.ents` — the full pre-arbitration set, overlaps included — rather than from the arbitrated `doc.ents`
6. Given a context similarity of 0.9 on a short entity and 0.3 on a longer overlapping one
   - when arbitration runs
     - then the longer one still wins — similarity is not consulted here

## Case handling (sort by length, first-claim-wins)

A single pass with a token-occupancy set. Each entity is accepted or rejected outright; nothing is merged, split, or re-scored. The decision is made purely on span geometry, and it is made *after* linking — so the expensive disambiguation may have run on entities that were then discarded on length alone.

## Later stages (deferred)

- **Length is not specificity.** Ranking by character count stands in for ontological specificity; the CDB knows the concept hierarchy (US 02 extracts it), but this step does not consult it.
- **Similarity is ignored in arbitration.** Folding `context_similarity` into the tie-break — or into the ranking itself — is the obvious improvement and is not implemented.
