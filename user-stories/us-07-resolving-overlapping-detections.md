# US 07 Resolving Overlapping Detections into One Annotation Set

As a *clinician analysing free-text notes*, I want to *get "diabetes mellitus type 2" as one single annotation, not three overlapping ones*, so that *each piece of text carries one clear meaning, and any later counting doesn't count the same thing twice*.

Finding candidates (US 05) is designed to find too many, on purpose: it walks through the text and records every complete name it passes, so spans that overlap or sit inside one another are completely normal, not a bug. Disambiguation (US 06) then removes candidates that fail its checks. But whatever is left can still overlap — and that's what this step fixes.

`create_main_ann` (`medcat/utils/postprocessing.py:37`) is the referee. Its rule is simple and mechanical: sort all the surviving matches by **text length, longest first**, then go through them one by one, keeping a match only if *none* of its words have already been claimed by a longer match that came before it. The longest match wins, and everything underneath it is thrown out.

Here's the catch: "longest" is being used as a stand-in for "most specific," and that stand-in isn't always right. Length is measured purely in characters of text — it says nothing about how confident the match was, or how well its context matched. So a long match with low confidence can beat a short match with high confidence, simply because they overlap, and the careful context-similarity work from US 06 plays no role in this decision at all. The full, unfiltered set of matches isn't thrown away completely — it stays available on `doc._.ents`, and turning on `general.show_nested_entities` (`medcat/config.py:378`) will show it — but by default, only the filtered set is returned.

## Acceptance Criteria

1. Given two surviving matches, where one's span completely contains the other's
   - when `create_main_ann` runs
     - then the longer one is kept, and the shorter one is removed from `doc.ents`
2. Given two matches that overlap by at least one shared word
   - when the arbitration runs
     - then the longer one wins, and the other is dropped completely — not shortened, not merged, just dropped
3. Given two overlapping matches of exactly the same length
   - when arbitration runs
     - then whichever one comes first in the sorted order wins — this tie-break has no deeper reasoning behind it
4. Given matches that don't overlap at all
   - when arbitration runs
     - then all of them are kept, in the order the sort produced
5. Given `general.show_nested_entities` is turned on
   - when the output is built (US 09)
     - then it comes from `doc._.ents` — the complete, unfiltered set including overlaps — instead of the filtered `doc.ents`
6. Given a short match with 0.9 context similarity overlaps a longer match with only 0.3
   - when arbitration runs
     - then the longer one still wins — similarity is not looked at during this step at all

## Case handling (sort by length, first claim wins)

This is a single pass that keeps track of which words are already "claimed." Each match is either kept whole or thrown out entirely — nothing is merged, split, or re-scored. The decision is based purely on the shape and length of the spans, and it happens *after* the linking step — so the expensive context-matching work in US 06 might already have run on entities that then get thrown away here for being too short.

## Later stages (deferred)

- **Length isn't the same as specificity.** Ranking by character count is a stand-in for "how specific is this concept," but the CDB actually knows the real concept hierarchy (built during US 02) — this step just doesn't check it.
- **Similarity is ignored during arbitration.** Using `context_similarity` as part of the tie-break, or the ranking itself, is an obvious improvement that hasn't been built yet.
