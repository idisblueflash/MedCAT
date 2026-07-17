# US 24 Opt-In Usage Monitoring

As an *operator*, I want to *log how a deployed model is actually being used, locally and only if I choose to turn it on*, so that *I can track usage without any data ever leaving my own infrastructure*.

`UsageMonitor` (`medcat/utils/usage_monitoring.py`, configured through `medcat.config.UsageMonitor`) keeps a small buffer of records — one per time the pipeline is called — and writes them out periodically to a log file. Each model gets its own log file, named using a configurable prefix plus the model's own content hash, so logs from different model versions never get mixed together.

This logging is turned off by default (`enabled: False`). When it's turned on, everything stays local: there's no network call at all, only writes to disk in a `log_folder` (with sensible OS defaults, like `~/.local/share/medcat/logs/` on Linux). There's also a third mode, `'auto'`, which lets an operator control logging centrally using two environment variables, `MEDCAT_USAGE_LOGS` and `MEDCAT_USAGE_LOGS_LOCATION`, instead of having to edit a config file separately on every machine. This matters if the same model pack is deployed across many machines at once.

## Acceptance Criteria

1. Given `enabled=False`
   - when the pipeline runs
     - then no logging happens at all, and no extra overhead is added
2. Given `enabled=True`
   - when enough events have accumulated
     - then they are written to `log_folder` in batches of `batch_size` (100 by default), instead of writing to disk on every single call
3. Given `enabled='auto'`
   - when MedCAT decides whether to log
     - then the on/off decision and the log location both come from the `MEDCAT_USAGE_LOGS` / `MEDCAT_USAGE_LOGS_LOCATION` environment variables, ignoring whatever `log_folder` was configured to
4. Given an older model pack and a newly retrained one
   - when both write usage logs
     - then their log filenames include each model's own hash, so the two sets of logs can be told apart

## Case handling (buffer events, then write them out in batches)

Each pipeline call is buffered in memory, then flushed in batches to a file named after the model's hash, in whichever location was resolved. The `'auto'` mode simply swaps "controlled by config file" for "controlled by environment variables," without changing how the writing itself works. The `UsageMonitor` settings class lives at `medcat/config.py:323-344`, exposed through `config.general.usage_monitor`, and is created using the running model's hash so log files always identify which model produced them.

## Later stages (deferred)

- **No log rotation or cleanup.** Log files currently grow without any limit per model. Rotating or deleting old logs by size or age would keep disk usage in check for long-running deployments.
- **No built-in reporting tool.** Logs are currently just raw per-model files. A small tool to summarize usage from them would save people from writing their own custom parsing scripts.
