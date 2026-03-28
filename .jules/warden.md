## 2025-02-21 — Assessment & Lifecycle

Observation / Pruned:
A subtle lifecycle risk was identified where poorly behaving subprocesses (such as those masking or ignoring `SIGTERM`) could cause indefinite hangs when a new file event triggered a process reload. If `self.current_process.wait()` blocked forever, the file watcher thread pool would starve and fail to process new events.

Alignment / Deferred:
Added a `timeout=0.25` bound to all `wait()` calls during subprocess termination, with a subsequent escalation to `SIGKILL` (via process groups) or `.kill()` (on Windows) to guarantee responsive operation. Documented the updated aggressive termination strategy in `README.md`. No dead code was pruned. Tagged and prepared release v0.1.1.
