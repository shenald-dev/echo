## 2024-05-24 — File watcher thread starvation via shared locks

Learning:
Using a single `threading.Lock()` to synchronize both short-lived operations (like debouncing timers in a file system event callback) and potentially long-running operations (like `process.wait()` on a subprocess) can cause thread starvation. When a slow-terminating subprocess held the lock, the main `watchdog` event loop was blocked, preventing the system from observing new file changes.

Action:
Always use dedicated, fine-grained locks for independent resources. In background-threaded architectures, ensure that event loops are never blocked by slow I/O or process management by separating their locking contexts.

## 2024-03-24 — Expensive Timer Overhead in Watchdog Events

Learning:
Spawning and cancelling `threading.Timer` inside a lock for every single file system event in Python creates a severe performance and memory churn bottleneck (taking ~0.3s for 1000 burst events).

Action:
Debounce rapid burst events using a single long-lived thread that sleeps until a `last_event_time` threshold is met, rather than starting and stopping threads on every event. This reduces overhead to O(1) time and space.

## 2025-02-21 — Ignoring Read-Only Events in Watchdog

Learning:
The `watchdog` library triggers redundant events on read-only operations like `opened` and `closed_no_write` (e.g., when running `cat` or IDE indexing). Failing to ignore these events results in unnecessary command executions and performance overhead.

Action:
Always explicitly check for and ignore `opened` and `closed_no_write` events (using `getattr(event, 'event_type', '')` for safety) in `watchdog` file system event handlers.

## 2025-02-21 — Robust Subprocess Termination

Learning:
When managing subprocesses, relying solely on `SIGTERM` and a blocking `.wait()` call can cause the parent process to hang indefinitely if the child process ignores the signal or hangs during cleanup.

Action:
Always use a timeout when waiting for a subprocess to terminate (e.g., `process.wait(timeout=0.25)`). If a `subprocess.TimeoutExpired` exception is caught, escalate to a forceful termination using `SIGKILL` (or `.kill()` on Windows) to guarantee the parent process can continue executing or shutdown cleanly.

## 2023-10-24 — File event debouncing reliability

Learning:
Using `time.time()` for tracking relative durations in the debounce worker creates a reliability risk. `time.time()` is vulnerable to system clock shifts (e.g. NTP syncs or user changes), which can cause the debounce `time_to_wait` calculation to become negative unexpectedly or pause for incorrectly long durations.

Action:
Always use `time.monotonic()` for tracking relative time intervals and durations within the application and tests to ensure stable, reliable execution independent of system clock changes.

## 2025-03-01 — Expensive wildcard fnmatch checks in hot paths

Learning:
Calling `fnmatch.fnmatch` inside a loop for wildcard filtering on high-volume file system events creates an O(N*M) performance bottleneck, as `fnmatch` evaluates patterns independently as strings.

Action:
Always pre-compile wildcard patterns into a single grouped regular expression using `re.compile("|".join(f"(?:{fnmatch.translate(p)})" for p in patterns))`. This reduces hot-path filtering complexity to O(N) by delegating evaluation to the optimized C regex engine.
## 2024-05-30 — Watchdog Ignore Matching Inaccuracy

Learning:
The `_is_ignored` pattern matching incorrectly split the file path by `/` and evaluated ignores via `isdisjoint()` directly against individual file segments. As a result, explicit folder paths (`src/foo.py`) or path-based wildcards (`build/*`) were not triggering proper exclusion. Watchdog also often prepends `./` to paths from the root, requiring strip operations before evaluation.

Action:
Evaluate exact string and wildcard regex ignores against the full relative path string *first* (stripping leading `./` where needed). Retain the path-segment loop solely for directory-wide fallbacks (e.g., `node_modules`).
