# US 08 Restricting Linking to a Subset of Concepts

As a *researcher running a study on a specific set of disorders*, I want to *restrict the model to only the concepts I care about*, so that *I get a focused set of annotations from a model trained on a whole ontology, without retraining it or filtering the results by hand afterwards*.

A full SNOMED or UMLS model knows millions of concepts, but a single study usually only cares about a few hundred of them. `LinkingFilters` (`medcat/config.py:466`) holds two lists: `cuis` (an allow-list) and `cuis_exclude` (a deny-list). The rule, enforced by `check_filters` (`medcat/config.py:497`, also `medcat/utils/filters.py:7`), is simple:

- If `cuis` is empty, everything is allowed, except whatever is on the deny-list.
- If `cuis` is not empty, only those concepts are allowed — and the deny-list still applies on top of that.

This means an empty allow-list means "no restriction at all," not "allow nothing." That distinction matters: if you accidentally leave the allow-list empty, the filter fails **open** (lets everything through) rather than **closed** (blocks everything).

There's a subtle timing issue worth knowing about. The filter is only checked at the very *end* of linking (US 06) — after disambiguation has already picked a winning concept. So it's possible for a filtered-out concept to win the comparison first, get removed by the filter afterward, and leave the mention with no annotation at all — even though a concept that *was* allowed scored second place. The setting `linking.filter_before_disamb` (`medcat/config.py:551`, used in `medcat/linking/vector_context_model.py:147`) fixes this by filtering the candidate list *before* picking a winner, so the best *allowed* concept wins instead. This changes the actual results, not just the speed — and it's turned off by default.

## Acceptance Criteria

1. Given both `filters.cuis` and `filters.cuis_exclude` are empty
   - when `check_filters` runs
     - then every concept passes — an unconfigured filter restricts nothing
2. Given `filters.cuis` contains a specific list of concepts
   - when linking runs
     - then only those concepts can be linked; every other concept the model knows is suppressed from the output
3. Given a concept appears in both `cuis` and `cuis_exclude`
   - when `check_filters` runs
     - then it is excluded — the deny-list always wins over the allow-list
4. Given a mention where the best-scoring candidate is filtered out, a second-place candidate is allowed, and `filter_before_disamb` is off (the default)
   - when linking runs
     - then the mention ends up with no annotation at all — the winner is picked first, and only rejected afterward
5. Given the same mention, but with `filter_before_disamb` turned on
   - when linking runs
     - then the filtered-out candidate is removed before scoring even starts, so the allowed second-place candidate is linked instead
6. Given a project filter is defined using `type_ids` instead of specific concept codes
   - when `get_project_filters` (`medcat/utils/filters.py:33`) expands them into actual CUIs
     - then it looks them up through `addl_info['type_id2cuis']`, and raises an error if that lookup table was never built (which happens if the CDB was made with `full_build=False`, see US 01)

## Case handling (allow-list and deny-list together, checked after the winner is picked)

Filtering is just a membership check — "is this concept on the list?" — with the convention that an empty allow-list means "allow everything." It's the very last check before an entity is accepted. During supervised training (US 11), several filters stack on top of each other: the model's own built-in filter, then the training project's filter, then an extra filter if one is supplied — with the expectation, written only as a code comment, that each one is a subset of the one before it. Nothing actually enforces that expectation in code.

## Later stages (deferred)

- **`filter_before_disamb` probably should be the default.** Filtering after picking a winner quietly loses recall in exactly the situation filters are meant to help with.
- **Filter settings are shared and can be changed by accident.** `config.linking.filters` gets modified in place during supervised training and restored afterward from a backup copy — if training crashes partway through, the model can be left holding one project's filter settings.
