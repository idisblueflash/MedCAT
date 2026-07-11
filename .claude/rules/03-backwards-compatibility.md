# Rule 03 — Serialized artifacts must stay backwards-compatible

**A CDB, Vocab, config, or model pack saved by an older MedCAT must still load in
a newer one, and a save/load round trip must not lose or corrupt data. This is
the MedCAT analogue of paper-degist's "never crash, never silently corrupt" — the
serialized model is MedCAT's manifest, and old models are real users' data.**

## The principle

Users train models that take hours and cost real data access, then pin a MedCAT
version and load that model for years. Breaking the load path — a renamed config
field, a changed pickle layout, a dropped attribute — silently strands those
models. CI enforces this with `tests/resources/model_compatibility/
check_backwards_compatibility.sh`; treat that script as a gate you can break, not
a formality.

## In practice

- **Round-trip is a test, not a hope.** Any change to `CDB`, `Vocab`, `Config`,
  or model-pack (de)serialization gets a test that saves with the new code and
  asserts the reloaded object is unchanged (`tests/test_cdb.py` already round-
  trips names, ontology tags, and type IDs — extend that pattern, don't replace
  it).
- **Adding a field:** give it a default and tolerate its absence on load, so an
  old artifact without the field still loads. Never make load raise on a missing
  new attribute.
- **Renaming/removing a field:** you cannot just delete it — keep a migration or
  a backwards-compatible alias on load, and route the removal through the
  deprecation policy (Rule 04). `examples/cdb_old_broken_weights_in_config.dat`
  exists precisely to test loading a known-old artifact — add a fixture like it
  for the state you are migrating from.
- **Config specifically stays pydantic-1 loadable** (Rule 01) — the config is the
  most-serialized object in the system.

## Why

MedCAT's value compounds only if a model trained today still loads tomorrow. The
compatibility script and round-trip tests are what let the code keep evolving
without invalidating every model already in the field — the same discipline that
lets paper-degist keep running when inputs change, applied to the artifact that
*is* MedCAT's output.
