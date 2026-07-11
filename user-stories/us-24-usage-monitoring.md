# US 24 Opt-In Usage Monitoring

As an *operator*, I want to *log how a deployed model is actually used, locally and opt-in*, so that *I can track usage without any data leaving my own infrastructure*.

`UsageMonitor` (`medcat/utils/usage_monitoring.py`, configured via `medcat.config.UsageMonitor`) buffers a record of pipeline invocations and periodically flushes them to a per-model log file named with a configurable `file_prefix` and the model's content hash, so logs from different model versions never collide.

Logging is off by default (`enabled: False`) and, when on, is entirely local: no network call, only writes to a `log_folder` on disk (OS-appropriate defaults such as `~/.local/share/medcat/logs/` on Linux). A third `'auto'` mode lets an operator control logging centrally via the `MEDCAT_USAGE_LOGS` / `MEDCAT_USAGE_LOGS_LOCATION` environment variables rather than editing a config file per deployment — which matters when one model pack is rolled out across many machines.

## Acceptance Criteria

1. Given `enabled=False`
   - when the pipeline runs
     - then no logging happens and no overhead is added
2. Given `enabled=True`
   - when events accumulate
     - then they are written to `log_folder` in batches of `batch_size` (default `100`) rather than one disk write per call
3. Given `enabled='auto'`
   - when logging is evaluated
     - then the on/off decision and location defer to `MEDCAT_USAGE_LOGS` / `MEDCAT_USAGE_LOGS_LOCATION`, ignoring the configured `log_folder`
4. Given an old and a newly retrained model pack
   - when both write usage logs
     - then their log filenames incorporate the model hash so the two can be told apart

## Case handling (buffer → batched local flush)

Invocations are buffered and flushed in batches to a hash-named file under the resolved location; the `'auto'` mode swaps config-driven control for environment-driven control without changing the write path. The `UsageMonitor` config class lives at `medcat/config.py:323-344`, exposed on the general config as `config.general.usage_monitor`, and is instantiated with the running model's hash so files self-identify their source model.

## Later stages (deferred)

- **Log rotation/retention.** Files grow unbounded per model; size/age-based rotation would bound disk use in long-running deployments.
- **Aggregation tooling.** Logs are raw per-model files; a small reporting utility would summarise usage without bespoke parsing.
