"""Shared behave hooks for the MedCAT BDD suite.

Features or scenarios tagged ``@wip`` (work in progress) are skipped, so the
suite stays green while step definitions are still being written. Remove the
``@wip`` tag from a feature once its steps are implemented and passing.
"""


def before_feature(context, feature):
    if "wip" in feature.tags:
        feature.skip("WIP: step definitions not yet implemented")


def before_scenario(context, scenario):
    if "wip" in scenario.tags:
        scenario.skip("WIP: step definitions not yet implemented")
