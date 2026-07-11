"""Step definitions for us-01-ner-and-linking.feature.

These are stubs: the feature is tagged ``@wip`` so behave skips it and none of
these run yet. They document the intended step signatures. To implement the
story, wire each step to a real ``CAT`` pipeline (e.g. build a small CDB/Vocab
fixture in ``context`` via ``before_all`` in environment.py) and remove the
``@wip`` tag from the feature.
"""

from behave import given, when, then


@given("a clinical document")
def step_a_clinical_document(context):
    raise NotImplementedError("pending: set context.text to a sample document")


@given("a name that maps to multiple CUIs")
def step_ambiguous_name(context):
    raise NotImplementedError("pending: set up an ambiguous name in the CDB")


@given('the addl_info keys "{key_a}" and "{key_b}" are requested')
def step_addl_info_requested(context, key_a, key_b):
    raise NotImplementedError("pending: record requested addl_info keys")


@given("only_cui is set to true")
def step_only_cui_true(context):
    context.only_cui = True


@given("a batch of documents")
def step_a_batch_of_documents(context):
    raise NotImplementedError("pending: set context.texts to a list of documents")


@when("get_entities runs the pipeline")
def step_run_get_entities(context):
    raise NotImplementedError("pending: call context.cat.get_entities(context.text)")


@when("the linker scores the candidates against the surrounding context")
def step_linker_scores_candidates(context):
    raise NotImplementedError("pending: run the pipeline over the ambiguous context")


@when("annotation runs")
def step_annotation_runs(context):
    raise NotImplementedError("pending: call get_entities with the configured options")


@when("get_entities_multi_texts runs")
def step_run_multi_texts(context):
    raise NotImplementedError("pending: call context.cat.get_entities_multi_texts(context.texts)")


@then("each detected entity is returned with its CUI, character offsets, and source name")
def step_entities_have_fields(context):
    raise NotImplementedError("pending: assert each entity has cui, start, end and source_value")


@then("the CUI whose learned context vector best matches is chosen, only above the similarity threshold")
def step_best_matching_cui_chosen(context):
    raise NotImplementedError("pending: assert the context-appropriate CUI was linked")


@then("each result additionally carries the requested cross-ontology references")
def step_results_have_cross_refs(context):
    raise NotImplementedError("pending: assert requested addl_info keys are present")


@then("the output is restricted to bare CUIs")
def step_output_bare_cuis(context):
    raise NotImplementedError("pending: assert only CUIs are returned")


@then("results are returned in the same order as the input documents")
def step_results_in_input_order(context):
    raise NotImplementedError("pending: assert output order matches input order")
