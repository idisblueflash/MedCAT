# US 09 Getting Structured Annotation Output for a Document

As a *developer integrating MedCAT into a pipeline*, I want to *get a document's annotations as a plain dictionary or JSON*, so that *I can store, index, or ship them without holding a spaCy `Doc` in memory or knowing anything about spaCy*.

`cat.get_entities(text)` runs the whole pipeline (US 04 → 05 → 06 → 07, plus the optional layers in US 13–15) and returns a dict keyed by entity id. Each entry carries the CUI, the CDB's preferred name, the exact source text that matched, the *detected name* (the normalised CDB form that actually fired — not the same as the source text), character offsets, semantic type ids and their names, and the context similarity exposed under both `acc` and `context_similarity`. If MetaCAT ran, `meta_anns` carries the negation / experiencer / temporality verdicts. `get_json` is the same thing serialised.

The single most useful and most overlooked field is the pair `source_value` / `detected_name`. `source_value` is what was in the note; `detected_name` is what the CDB matched after normalisation and possible spell-correction (US 04). When they diverge, that divergence *is* the audit trail — the only place a wrongly-fired spell-correction becomes visible. Note that `acc` is not a probability: it is a cosine-similarity blend, and for a direct (single-candidate) link it is hard-coded to `1` without any vector being computed.

## Acceptance Criteria

1. Given a document with linked entities
   - when `get_entities` runs
     - then each entity yields `cui`, `pretty_name`, `source_value`, `detected_name`, `start`, `end`, `type_ids`, `types`, `acc`, `context_similarity`, `id`, and a (possibly empty) `meta_anns`
2. Given `addl_info=['cui2icd10', 'cui2snomed', ...]`
   - when annotation runs
     - then each requested map is looked up in `cdb.addl_info` and attached under the key after the `2` (`icd10`, `snomed`) — silently empty if the CDB was built without `full_build`
3. Given `only_cui=True`
   - when output is built
     - then the entity dict collapses to `{id: cui}` and everything else is dropped
4. Given a directly-linked entity (single unambiguous candidate)
   - when output is built
     - then `acc` is `1` and no similarity was actually computed — the value is an assertion, not a measurement
5. Given `annotation_output.context_left` / `context_right` are set
   - when output is built
     - then the surrounding tokens are included per entity, making an annotation reviewable without re-fetching the source document
6. Given `general.show_nested_entities` is on
   - when output is built
     - then it is drawn from the un-arbitrated entity list (US 07) and will contain overlapping spans
7. Given a `None` document (a failed batch member, US 17)
   - when output is built
     - then an empty `{'entities': {}, 'tokens': []}` is emitted rather than an exception, preserving position in the output list

## Case handling (project the doc, never re-decide)

This step makes no decisions. Every field is read straight off the spaCy `Doc` the pipeline produced; the only branching is over what the caller asked to include. Anything absent from the output was dropped earlier — by threshold (US 06), by filter (US 08), or by overlap arbitration (US 07) — and this layer does not record which.

## Later stages (deferred)

- **No rejection trace.** An entity dropped below threshold in US 06 is indistinguishable in the output from one never detected. A `rejected` list would make failures diagnosable.
- **`acc` is overloaded.** It means "cosine blend" for disambiguated entities and "1, trust me" for direct links; consumers cannot tell these apart.
