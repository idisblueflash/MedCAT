"""Step definitions for us-09-structured-annotation-output.feature.

These are stubs: the feature is tagged ``@wip`` so behave skips it and none of
these run yet. They document the intended step signatures. To implement the
story, wire each step to a real ``CAT`` pipeline (e.g. build a small CDB/Vocab
fixture in ``context`` via ``before_all`` in environment.py) and remove the
``@wip`` tag from the feature.
"""

from behave import given, when, then


@given("a document with linked entities")
def step_document_with_entities(context):
    raise NotImplementedError("pending: set context.text to a document that links entities")


@given('the addl_info keys "{key_a}" and "{key_b}" are requested')
def step_addl_info_requested(context, key_a, key_b):
    context.addl_info = [key_a, key_b]


@given("only_cui is set to true")
def step_only_cui_true(context):
    context.only_cui = True


@given("a directly-linked entity with a single unambiguous candidate")
def step_direct_link(context):
    raise NotImplementedError("pending: set up a name with exactly one candidate CUI")


@given("a None document from a failed batch member")
def step_none_document(context):
    context.text = None


@when("get_entities runs")
def step_run_get_entities(context):
    raise NotImplementedError("pending: context.result = context.cat.get_entities(context.text)")


@when("annotation runs")
def step_annotation_runs(context):
    raise NotImplementedError("pending: call get_entities with context.addl_info")


@when("output is built")
def step_output_built(context):
    raise NotImplementedError("pending: build the output dict with the configured options")


@then("each entity yields cui, pretty_name, source_value, detected_name, start, end, type_ids, types, acc, context_similarity, id, and a meta_anns field")
def step_entity_full_fields(context):
    raise NotImplementedError("pending: assert every listed key is present on each entity")


@then('each requested map is attached under the key after the "2", or is empty when the CDB was built without full_build')
def step_cross_ontology_maps(context):
    raise NotImplementedError("pending: assert icd10/snomed keys attached (or empty without full_build)")


@then("each entity collapses to its id mapped to a cui and everything else is dropped")
def step_only_cui_collapsed(context):
    raise NotImplementedError("pending: assert output is {id: cui} with no other fields")


@then("acc is 1 and no similarity was actually computed")
def step_direct_link_acc(context):
    raise NotImplementedError("pending: assert acc == 1 for the direct link")


@then("an empty entities-and-tokens structure is emitted instead of raising")
def step_empty_output(context):
    raise NotImplementedError("pending: assert output == {'entities': {}, 'tokens': []}")
