## 2026-04-16 — Watcher Process Termination Logic

Learning:
The POSIX signal checking (`process.returncode == -15`) masked legitimate user command crashes. We can safely remove it in favor of checking the `_echo_terminated` flag because the `_terminate_process` method explicitly sets this attribute on the process object *before* it returns or escalates, regardless of platform (`self.is_posix` conditional blocks). However, sleep-based debouncing tests were brittle.

Action:
Ensure testing durations account for scheduling overhead but avoid massive overall CI slowdowns.

2024-04-16 — Trailing Slashes in Ignore Patterns
Learning: Directory ignore patterns supplied with trailing slashes (e.g., `build/`) fail to match because internal paths are normalized without them.
Action: Ensure `ignore_patterns` list comprehensions strip trailing slashes (`.rstrip('/')`) alongside other normalizations to guarantee robust matching.

## 2026-04-17 — Eager Evaluation & Intent Flag Placement

Learning:
Eager evaluation inside `watchdog` hot paths (like `on_any_event`) causes redundant cache lookups and array iterations. Specifically, evaluating `_is_ignored(dest_path)` before checking if `src_path` is ignored costs CPU time for every valid "moved" file event. Also, placing intent flags (like `setattr(process, '_echo_terminated', True)`) *after* the OS termination call is unsafe: if the process exits right before termination and throws `OSError`, the intent flag is never set.

Action:
Always lazy-evaluate expensive filters in event-loop hot paths. Always set intent flags *before* executing fallible OS-level state changes to guarantee accurate state tracking in exception handlers.

## 2026-04-17 — Dead Code in Reload Termination Feedback

Learning:
When managing subprocesses, if a reload starts a new process, the class attribute `self.current_process` is reassigned immediately. Therefore, in the wait block of the *old* process, checking `self.current_process is process` will evaluate to `False`. This renders any termination reporting logic nested within that block as dead code, leading to silent reloads.

Action:
Evaluate termination flags (`_echo_terminated`) independently of the "current process" identity check to ensure the correct system feedback is provided regardless of race conditions during reassignment.

## 2024-04-18 — Process Termination Reporting Dead Code

Learning:
When evaluating a subprocess's intent-based termination flags after `process.wait()`, guarding the reporting logic with `self.current_process is process` causes it to become dead code. During a command reload, `self.current_process` is reassigned to the new process before the old process's wait block completes, thus failing to report successful execution or failure.

Action:
Ensure post-termination reporting logic unconditionally logs the outcome when the intention-based check (`_echo_terminated`) is not met, instead of restricting it to the current process reference.

## 2026-04-18 — Redundant Ignore Evaluation Optimization

Learning:
In hot paths like `_is_ignored_impl` inside `watchdog` loops, repetitive checks that perform operations already inherently satisfied by earlier checks cost unnecessary CPU cycles. For example, explicitly evaluating whether the first directory layer `parts[0]` matches exact ignores and wildcards is wasteful, as `exact_ignores.isdisjoint(parts)` and iterating over `parts` already validates it earlier in the function.

Action:
Avoid redundant state re-evaluation on subsets of data in the file watcher's hot path by explicitly reviewing the cascade of earlier boolean checks.

## 2026-04-20 — Path Normalization Hot-Path Bottleneck

Learning:
`watchdog` file watchers trigger events with absolute paths. Converting these absolute paths back to relative paths relative to the watch directory `base_path` using `os.path.relpath()` is computationally expensive (approx 10-15x slower than a simple slice). During high-volume file events (like `npm install` or branch changes), this overhead chokes the hot path and introduces measurable lag before commands execute.

Action:
When implementing `watchdog` ignore filters, normalize absolute event paths to relative paths against the watched `base_path` to ensure wildcard patterns match correctly. For optimal performance, pre-compute the absolute base path with a trailing separator and use a fast string slice (`if path.startswith(self._abs_base_path): path = path[len(self._abs_base_path):]`) before falling back to `os.path.relpath` (wrapped in a `try/except ValueError`).
## 2026-04-21 — Fix path prefix accumulation bug in file ignore logic

Learning:
An off-by-one bug in array slicing (`parts[1:-1]`) during path matching caused the file watcher to skip exact matching against the full, multi-part path itself. This falsely allowed events on ignored files to trigger commands when the target file path was within a matched ignore directory.

Action:
Ensure accumulation loops over path components include all elements of the sequence up to the leaf node (i.e., using `parts[1:]`) so that multi-part file patterns are reliably validated against exact ignores.

## 2026-04-22 — Stream Redirection & Regex Parsing

Learning:
When providing `stdout` or `stderr` arguments to `subprocess.Popen`, passing `sys.stdout` or `sys.stderr` directly causes a crash (`io.UnsupportedOperation: fileno`) in test environments (e.g., pytest's `capsys`) or GUI wrappers where the streams lack a `.fileno()` method. Additionally, when identifying wildcard patterns for `fnmatch` evaluation, character class brackets `[` must be checked alongside `*` and `?`, otherwise patterns like `[a-z].tmp` are incorrectly treated as exact match strings.

Action:
Always wrap custom stream targets with a safety check for `.fileno()`, falling back to `None` to safely inherit system-level descriptors. Always include `[` when distinguishing wildcard paths from static paths.
## 2026-04-22 — Ignore Pattern Caching and Redundancy

Learning:
Inside the `_is_ignored_impl` hot path, `normalized_path in self.exact_ignores` and `self.wildcard_regex.match(normalized_path)` are inherently redundant. `isdisjoint()` evaluates every split part individually. When `normalized_path` itself has no slashes, it is `parts[0]` and caught there. When `normalized_path` contains slashes, the `if len(parts) > 1:` loop explicitly rebuilds the exact same string on the final iteration (e.g. `foo/bar` becomes `prefix` on final loop) and matches it.

Action:
Removed the top-level checks to save string hashing and regex matching latency on deep recursive paths.

## 2026-04-23 — Fix _abs_base_path to properly use os.path.join and handle root directory matching

Learning:
Using string concatenation with `os.sep` for `_abs_base_path` can cause issues when `os.path.abspath` returns a path that already has a separator (e.g. root directory `/`), resulting in `//` and failing the prefix check in `_is_ignored_impl`.

Action:
Use `os.path.join(os.path.abspath(base_path), '')` to safely handle trailing separators, and update `_is_ignored_impl` to check if `path` exactly matches `self._abs_base_path` (e.g. root directory). This prevents expensive `os.path.relpath` fallbacks for valid ignore pattern matching.
## 2026-04-23 — Ignore Pattern Caching and Redundancy

Learning:
Inside the `_is_ignored_impl` hot path, `normalized_path in self.exact_ignores` and `self.wildcard_regex.match(normalized_path)` are inherently redundant. `isdisjoint()` evaluates every split part individually. When `normalized_path` itself has no slashes, it is `parts[0]` and caught there. When `normalized_path` contains slashes, the `if len(parts) > 1:` loop explicitly rebuilds the exact same string on the final iteration (e.g. `foo/bar` becomes `prefix` on final loop) and matches it.

Action:
Removed the top-level checks to save string hashing and regex matching latency on deep recursive paths.

## 2026-04-24 — CPU Spin Bug in File Watcher Debounce Worker

Learning:
If the `_debounce_worker` thread receives an event with no valid `path_to_run` (e.g. from an ignored file or empty path string) and `time_to_wait` reaches `<= 0`, it skips the execution block and attempts to `wait` on the shutdown event. Because `time_to_wait <= 0`, `wait(timeout)` returns immediately, causing an infinite while-loop that consumes 100% CPU. Additionally, `on_any_event` allowed falsely truthy null-path events to spawn the debounce thread.

Action:
Ensure the background `_debounce_worker` thread unconditionally terminates (via `return`) when `time_to_wait <= 0`, executing the command only if the path is valid and no shutdown is requested. Added early returns in `on_any_event` to prevent spawning timers for invalid paths entirely.

## 2026-04-24 — Test Suite Thread Synchronization Reliability

Learning:
Tests involving thread execution (like the file watcher's debounce or shutdown threads) must not rely on `time.sleep()` for waiting. Under CI/coverage load, these static sleeps are prone to flakiness due to scheduling overhead, causing assertions against thread termination state to falsely fail.


## 2026-04-24 — Test Suite Dynamic Polling Fix

Learning:
Using `.join()` unconditionally to replace `time.sleep()` in test cases is a flawed approach because `join()` halts the test thread until the target thread completely finishes its execution. For file watcher tests involving processes that are expected to be running or terminating, the assertions need to test an intermediate state. Unconditional joins bypass this intermediate state and test the end state, missing the intent.

Action:
Instead of `time.sleep()`, tests should use dynamic polling mechanisms (`while handler.current_process is None` coupled with short `time.sleep(0.05)` cycles and a maximum timeout) to efficiently wait only until the desired intermediate condition is met. This ensures the tests run significantly faster while preventing flakiness.
