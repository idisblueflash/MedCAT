"""Step definitions for us-01-building-concept-database-from-csv.feature.

These steps drive the real ``CDBMaker.prepare_csvs`` entry point. Each scenario
builds a small, self-describing concept fixture as an in-memory DataFrame (which
``prepare_csvs`` accepts in place of a CSV path), so no on-disk fixtures are
needed. The spaCy-backed ``CDBMaker`` is built once and reused, because loading
the model is the slow part.

The regex step matcher is used so that a quoted field can capture an empty
string (e.g. a row whose ``cui`` is ""); the module resets the matcher back to
the default ``parse`` at the end so other step modules are unaffected.
"""

import logging
import tempfile

import pandas as pd
from behave import given, when, then, use_step_matcher

from medcat.cdb import CDB
from medcat.cdb_maker import CDBMaker
from medcat.config import Config

use_step_matcher("re")

_MAKER = None


def _maker():
    """Build the spaCy-backed CDBMaker once and reuse it across scenarios.

    Returns:
        CDBMaker: A shared maker; its CDB is reset before each build.
    """
    global _MAKER
    if _MAKER is None:
        config = Config()
        config.general["spacy_model"] = "en_core_web_md"
        _MAKER = CDBMaker(config)
    return _MAKER


class _WarningCollector(logging.Handler):
    """Collects the warning messages emitted while a CDB is being built."""

    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def _build(context, df, full_build=False):
    """Reset the shared CDB, build it from one DataFrame, and capture warnings.

    Args:
        context: The behave scenario context.
        df (pd.DataFrame): The concept rows for this scenario.
        full_build (bool): Whether to populate ``addl_info`` (Default value False).

    Returns:
        CDB: The freshly built CDB, also stored on ``context.cdb``.
    """
    maker = _maker()
    maker.reset_cdb()
    logger = logging.getLogger("medcat.cdb_maker")
    collector = _WarningCollector()
    previous_level = logger.level
    logger.setLevel(logging.WARNING)
    logger.addHandler(collector)
    try:
        cdb = maker.prepare_csvs([df], full_build=full_build)
    finally:
        logger.removeHandler(collector)
        logger.setLevel(previous_level)
    context.cdb = cdb
    context.warnings = collector.messages
    return cdb


@given(r'a CSV where three rows share the CUI "(?P<cui>[^"]*)" with the names "(?P<name_a>[^"]*)", "(?P<name_b>[^"]*)", and "(?P<name_c>[^"]*)"')
def step_three_rows_one_cui(context, cui, name_a, name_b, name_c):
    context.df = pd.DataFrame({
        "cui": [cui, cui, cui],
        "name": [name_a, name_b, name_c],
    })


@given(r'a CSV that supplies only the CUI "(?P<cui>[^"]*)" and the name "(?P<name>[^"]*)"')
def step_cui_and_name_only(context, cui, name):
    context.df = pd.DataFrame({"cui": [cui], "name": [name]})


@given(r'a full-build CSV concept "(?P<cui>[^"]*)" named "(?P<name>[^"]*)" in ontology "(?P<ontology>[^"]*)" with type IDs "(?P<type_ids>[^"]*)"')
def step_full_build_concept(context, cui, name, ontology, type_ids):
    context.full_build = True
    context.df = pd.DataFrame({
        "cui": [cui],
        "name": [name],
        "ontologies": [ontology],
        "name_status": ["P"],
        "type_ids": [type_ids],
        "description": ["A worked clinical example concept."],
    })


@given(r'a CSV row whose CUI is "(?P<cui>[^"]*)" and whose name is "(?P<name>[^"]*)"')
def step_single_row(context, cui, name):
    context.df = pd.DataFrame({"cui": [cui], "name": [name]})


@when(r"prepare_csvs builds the CDB")
def step_prepare_csvs(context):
    _build(context, context.df, getattr(context, "full_build", False))


@when(r"the CDB is saved and reloaded")
def step_save_and_reload(context):
    cdb = _build(context, context.df, getattr(context, "full_build", False))
    with tempfile.NamedTemporaryFile(suffix=".dat") as f:
        cdb.save(f.name)
        context.reloaded = CDB.load(f.name)


@then(r'the CDB holds one concept "(?P<cui>[^"]*)" whose names are "(?P<name_a>[^"]*)", "(?P<name_b>[^"]*)", and "(?P<name_c>[^"]*)"')
def step_one_merged_concept(context, cui, name_a, name_b, name_c):
    assert list(context.cdb.cui2names) == [cui], context.cdb.cui2names
    assert context.cdb.cui2names[cui] == {name_a, name_b, name_c}, context.cdb.cui2names[cui]


@then(r'the build succeeds and concept "(?P<cui>[^"]*)" has no type IDs')
def step_build_succeeds_no_type_ids(context, cui):
    assert cui in context.cdb.cui2names, context.cdb.cui2names
    assert context.cdb.cui2type_ids[cui] == set(), context.cdb.cui2type_ids[cui]


@then(r'concept "(?P<cui>[^"]*)" keeps its names, the ontology tag "(?P<ontology>[^"]*)", and the type IDs "(?P<type_a>[^"]*)" and "(?P<type_b>[^"]*)"')
def step_round_trip_preserved(context, cui, ontology, type_a, type_b):
    reloaded = context.reloaded
    assert reloaded.cui2names == context.cdb.cui2names, reloaded.cui2names
    assert reloaded.cui2type_ids[cui] == {type_a, type_b}, reloaded.cui2type_ids[cui]
    assert reloaded.addl_info["cui2ontologies"][cui] == {ontology}, reloaded.addl_info["cui2ontologies"].get(cui)


@then(r"a malformed-row warning is emitted and no concept is added")
def step_malformed_reported(context):
    assert any("malformed" in message.lower() for message in context.warnings), context.warnings
    assert context.cdb.cui2names == {}, context.cdb.cui2names


# Restore the default matcher so other step modules keep using parse-style steps.
use_step_matcher("parse")
