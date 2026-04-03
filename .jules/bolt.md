## 2025-02-18 — Fast Path Evaluation Cache

Learning:
The `_is_ignored` function handles rapid string normalization, iteration over directory structures, and regex lookups for every single file system event intercepted by the watchdog. Because bulk operations (like `npm install` or massive text replacement) can fire thousands of events in milliseconds, evaluating ignores redundantly creates significant CPU overhead on hot paths.

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
## 2025-03-08 — Expensive Ignore Checks on Repeated File Paths

Learning:
Running complex ignore path checks (involving regular expression matching and string manipulation) on every file system event (creation, modification, etc.) creates a significant performance bottleneck, especially during burst events or when interacting with large directories.

Action:
Utilize `functools.lru_cache` to cache the results of path ignore checks. This drastically reduces CPU overhead by bypassing the expensive matching logic for repeatedly processed paths, turning an O(N) operation into an O(1) cache lookup for warm paths.
