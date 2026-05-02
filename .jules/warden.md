@@ -12,159 +12,19 @@ Observation / Pruned:
 A regression was identified where complex wildcard ignore patterns (like `src/*.tmp` or `build/*`) failed to match correctly due to the regex operating on individual path parts instead of the full normalized path.

 Alignment / Deferred:
-Updated the `_is_ignored` fast-path filter to normalize paths and check both exact and wildcard patterns against the full relative path before falling back to component intersection. Added unit tests for complex wildcard patterns. Prepared patch release v0.1.5.
+Updated the `_is_ignored` fast-path filter to normalize paths and check both exact and wildcard patterns against the ful

-## 2025-02-21 — Assessment & Lifecycle
+// ... 10798.8 characters truncated (middle section) ...

-Observation / Pruned:
-A subtle lifecycle risk was identified where poorly behaving subprocesses (such as those masking or ignoring `SIGTERM`) could cause indefinite hangs when a new file event triggered a process reload. If `self.current_process.wait()` blocked forever, the file watcher thread pool would starve and fail to process new events.
-
-Alignment / Deferred:
-Added a `timeout=0.25` bound to all `wait()` calls during subprocess termination, with a subsequent escalation to `SIGKILL` (via process groups) or `.kill()` (on Windows) to guarantee responsive operation. Documented the updated aggressive termination strategy in `README.md`. No dead code was pruned. Tagged and prepared release v0.1.1.
-
-## 2026-03-27 — Assessment & Lifecycle
-
-Observation / Pruned:
-Cleaned up `test_dir/` containing dummy files which were artifacts left behind by the previous agent's run. No functional or production changes were made.
-
-Alignment / Deferred:
-Version bumped to `0.1.2` as a patch release reflecting the cleanup.
-
-## 2026-04-01 — Assessment & Lifecycle
-
-Observation / Pruned:
-Verified structural soundness of the debounce logic that leverages `time.monotonic()`. Dead code elimination and linter passed smooth