# US 14 Opt-In Usage Monitoring

This specification describes MedCAT's local, opt-in usage-logging facility, which lets an operator track how a deployed model is actually being used without any data leaving their own infrastructure.

## Core Purpose

`UsageMonitor` (`medcat/utils/usage_monitoring.py`, configured via `medcat.config.UsageMonitor`) buffers a record of pipeline invocations and periodically flushes them to a per-model log file named with a configurable `file_prefix` and the model's content hash, so logs from different model versions never collide in the same file.

## Key Design Consideration

Logging is off by default (`enabled: False`) and, when turned on, is entirely local: there is no network call, only writes to a `log_folder` on disk (OS-appropriate defaults such as `~/.local/share/medcat/logs/` on Linux). A third `'auto'` mode additionally lets an operator control logging centrally through the `MEDCAT_USAGE_LOGS` / `MEDCAT_USAGE_LOGS_LOCATION` environment variables rather than editing a config file per deployment, which matters when the same model pack is rolled out across many machines.

## Acceptance Criteria Summary

The specification requires:
- `enabled=False` performs no logging and adds no overhead
- `enabled=True` writes buffered events to `log_folder` in batches of `batch_size` (default `100`) rather than one disk write per call
- `enabled='auto'` defers the on/off decision and log location to the `MEDCAT_USAGE_LOGS` / `MEDCAT_USAGE_LOGS_LOCATION` environment variables, ignoring the configured `log_folder` in that mode
- Log filenames incorporate the model's hash, so usage from an old and a newly retrained model pack can be told apart

## Implementation Notes

The `UsageMonitor` config class lives at `medcat/config.py:323-344` and is exposed on the general config as `config.general.usage_monitor`; the monitor itself is instantiated with the running model's hash so log files self-identify which model produced them.
