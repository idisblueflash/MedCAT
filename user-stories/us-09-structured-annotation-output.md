# US 09 Getting Structured Annotation Output for a Document

As a *developer integrating MedCAT into a pipeline*, I want to *get a document's annotations as a plain dictionary or JSON*, so that *I can store, search, or send them onward without keeping a spaCy `Doc` object in memory, and without needing to know anything about spaCy*.

`cat.get_entities(text)` runs the whole pipeline in order (normalising in US 04, detecting in US 05, disambiguating in US 06, resolving overlaps in US 07 — plus any optional extra layers from US 13–15) and returns a dictionary, one entry per found entity. Each entry includes:

- the concept code (`cui`)
- the CDB's preferred name for it
- the exact text that was matched in the note (`source_value`)
- the *detected name* — the cleaned-up CDB form that actually matched (not the same as the raw source text)
- character positions (where it starts and ends)
- semantic type codes and their names
- the context similarity score, available under two names: `acc` and `context_similarity`

If MetaCAT ran (US 13), there's also a `meta_anns` field with things like negation, who experienced it, and when. `get_json` gives you the same information as a JSON string instead of a dictionary.

The single most useful, and most often overlooked, pair of fields is `source_value` and `detected_name`. `source_value` is exactly what was written in the note. `detected_name` is what the CDB actually matched, after cleanup and possible spelling correction (US 04). When these two differ, that difference is your audit trail — it's the only place where you can spot a spelling "correction" that fired when it shouldn't have. Also worth knowing: `acc` is not a real probability. It's a similarity score, and for a direct link (only one possible candidate) it is simply hard-coded to `1`, without any actual vector comparison happening.

## Acceptance Criteria

1. Given a document with linked entities
   - when `get_entities` runs
     - then each entity includes `cui`, `pretty_name`, `source_value`, `detected_name`, `start`, `end`, `type_ids`, `types`, `acc`, `context_similarity`, `id`, and a `meta_anns` field (which may be empty)
2. Given `addl_info=['cui2icd10', 'cui2snomed', ...]` is requested
   - when annotation runs
     - then each requested lookup table is pulled from `cdb.addl_info` and attached under a shorter key (`icd10`, `snomed`) — quietly left empty if the CDB wasn't built with `full_build` turned on
3. Given `only_cui=True`
   - when the output is built
     - then each entity is shrunk down to just `{id: cui}`, and everything else is dropped
4. Given a directly-linked entity (only one possible candidate, so no comparison was needed)
   - when the output is built
     - then `acc` is set to `1`, even though no similarity was actually calculated — this value is an assumption, not a measurement
5. Given `annotation_output.context_left` / `context_right` are set
   - when the output is built
     - then the surrounding words are included for each entity, so you can review an annotation without having to reopen the original document
6. Given `general.show_nested_entities` is turned on
   - when the output is built
     - then it comes from the unfiltered entity list (US 07) and will include overlapping spans
7. Given a document is `None` (meaning it failed to process during batch processing, US 17)
   - when the output is built
     - then an empty result — `{'entities': {}, 'tokens': []}` — is returned instead of an error, so its position in the output list is preserved

## Case handling (report what happened — never decide anything new)

This step makes no decisions of its own. Every field is simply read off the spaCy `Doc` object the pipeline already produced; the only real choice here is which fields the caller asked to include. If an entity is missing from the output, it was dropped earlier — by the similarity threshold (US 06), by a filter (US 08), or by overlap resolution (US 07) — and this step doesn't record which one was responsible.

## Later stages (deferred)

- **No record of rejections.** An entity dropped for scoring too low in US 06 looks exactly the same in the output as one that was never detected at all. A separate `rejected` list would make these failures much easier to diagnose.
- **`acc` means two different things.** For a disambiguated entity it's a real similarity score; for a direct link it's just "1, trust me." Right now there's no way to tell these two cases apart from the output alone.
