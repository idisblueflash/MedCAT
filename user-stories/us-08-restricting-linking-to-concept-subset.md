# US 08 Restricting Linking to a Subset of Concepts

As a *researcher running a study on a specific set of disorders*, I want to *restrict the model to the concepts I care about*, so that *I get a focused annotation set from a model trained on a whole ontology without retraining or post-filtering by hand*.

A full SNOMED or UMLS model knows millions of concepts; a study usually wants a few hundred. `LinkingFilters` (`medcat/config.py:466`) holds two sets — `cuis` (an allow-list) and `cuis_exclude` (a deny-list) — and `check_filters` (`medcat/config.py:497`, also `medcat/utils/filters.py:7`) applies one rule: if `cuis` is empty, everything is allowed except the excluded; if `cuis` is non-empty, only those are allowed, and the exclusion still applies on top. Empty allow-list means "no restriction", not "allow nothing" — a distinction that matters because an accidentally-empty filter fails **open**, not closed.

The filter is consulted at the *end* of linking (US 06) — after disambiguation has already picked a winner. So a filtered-out CUI can still win the argmax and take the mention with it, then be dropped, leaving the mention unannotated even though a permitted candidate scored second. `linking.filter_before_disamb` (`medcat/config.py:551`, applied at `medcat/linking/vector_context_model.py:147`) flips this — filtering the candidate list before the argmax so the best *permitted* candidate wins — and it changes results, not just runtime. It defaults to off.

## Acceptance Criteria

1. Given `filters.cuis` and `filters.cuis_exclude` are both empty
   - when `check_filters` runs
     - then every CUI passes — an unconfigured filter restricts nothing
2. Given `filters.cuis` holds a set of CUIs
   - when linking runs
     - then only those CUIs are linkable; every other concept the model knows is suppressed at output
3. Given a CUI in both `cuis` and `cuis_exclude`
   - when `check_filters` runs
     - then it is excluded — the deny-list wins
4. Given a mention whose best-scoring candidate is filtered out, a permitted candidate scores second, and `filter_before_disamb` is off (default)
   - when linking runs
     - then the mention is annotated with nothing — the winner is chosen first, then rejected
5. Given the same mention with `filter_before_disamb` on
   - when linking runs
     - then the filtered candidate is removed before scoring and the permitted second-place candidate is linked
6. Given a project filter defined as `type_ids` rather than CUIs
   - when `get_project_filters` (`medcat/utils/filters.py:33`) expands them
     - then it resolves them through `addl_info['type_id2cuis']`, raising if that map was never built (i.e. the CDB was made with `full_build=False`, US 01)

## Case handling (allow-list ∩ deny-list, applied post-argmax)

Filtering is a set-membership test with an empty-means-all convention, applied as the last gate before an entity is accepted. During supervised training (US 11) filters are layered — the model's own config filter, then the annotation project's filter, then an `extra_cui_filter` — with the documented expectation `extra_cui_filter ⊆ MCT filter ⊆ model filter`. Nothing enforces that expectation; it is a comment.

## Later stages (deferred)

- **`filter_before_disamb` should probably be the default.** The post-argmax default silently costs recall in exactly the situation filters are used for.
- **Filter state is global and mutable.** `config.linking.filters` is mutated in place during supervised training and restored afterwards from a saved copy — an exception mid-training leaves the model holding a project's filters.
