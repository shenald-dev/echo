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

## 2026-04-24 — Rich Markup Error Bug

Learning:
When passing raw user strings containing square brackets (like file paths, directories, or bash commands) into `rich.console.print` format strings, `rich` attempts to parse them as style markup tags (e.g., `[red]`). If the string inside the brackets is not a valid tag, or if there's a typo/unclosed tag, the library throws a `MarkupError` exception which will crash the thread executing the print statement.

Action:
Always use `rich.markup.escape(str(variable))` before injecting unvalidated user-provided strings into `rich` print statements to guarantee safe output.

## 2026-04-28 — Pre-computing `_base_prefix` for Fast-Path Slicing

Learning:
Inside the `_is_ignored_impl` hot path in `watchdog`, calling `os.path.relpath` for relative event paths when they could be sliced using `len(self._base_prefix)` introduced measurable latency in high-volume events. Additionally, generically calling `.removeprefix('./')` on paths could cause unexpected resolution regressions.

Action:
Pre-compute `_base_prefix` during initialization (`os.path.join(self.base_path, '')`) and use it in `startswith()` alongside `_abs_base_path` for fast string slicing. Also removed the blind `.removeprefix('./')` behavior to improve robustness.

## 2026-04-29 — Reliability Fix for SIGTERM

Learning:
Command-line file watchers and daemon tools usually listen for KeyboardInterrupt (SIGINT) to clean up subprocesses gracefully. However, they often ignore SIGTERM, which is the standard termination signal sent by containers (Docker/K8s) and process managers. Ignoring SIGTERM causes the main watcher to die instantly, leaking running child processes in the background indefinitely and causing resource exhaustion.

Action:
Always register a SIGTERM handler on POSIX systems (`if platform.system() != "Windows"`) that performs the same graceful shutdown and subprocess termination steps as the KeyboardInterrupt handler.

## 2026-04-29 — Ignore Filter Relpath & Compound Loop Overhead

Learning:
Inside the `_is_ignored_impl` hot path, `os.path.relpath` is computationally expensive because it inherently resolves absolute paths. While optimizations existed for exact prefix matching, simple relative paths (e.g., `src/file.py`) against a `.` base path would fall through and trigger a `relpath` call, slowing down high-volume events. Additionally, reconstructing cumulative directory prefixes (`foo`, `foo/bar`) to test against exact/wildcard ignores consumes significant CPU cycles and is entirely unnecessary if the user specified no compound ignore patterns (i.e., no slashes in any pattern).

Action:
In `watchdog` event path normalization, bypass the computationally expensive `os.path.relpath` for the common case where `base_path` is `.` and the path is already relative by adding a fast-path condition: `elif self.base_path == "." and not os.path.isabs(path) and not path.startswith(".."): pass`.
To optimize ignore pattern matching in hot loops, pre-compute a flag during initialization (e.g., `self._has_compound_ignores = any('/' in p for p in self.ignore_patterns)`) and use it to short-circuit the evaluation of compound directory paths if no slash-based ignore patterns exist.

## 2026-05-01 — Wildcard Regex Split Optimization

Learning:
Inside the file watcher's `_is_ignored_impl` hot path, applying a combined wildcard regex that includes both simple patterns (e.g. `*.tmp`) and compound patterns (e.g. `src/*.tmp`) to individual path segments (`parts`) and cumulative directory prefixes (`prefix`) is redundant and computationally wasteful. A simple wildcard pattern incorrectly evaluated against a cumulative prefix path loop wastes time, and a compound wildcard will never match a simple directory segment.

Action:
Split wildcard patterns into `simple_wildcards` (no slashes) and `compound_wildcards` (contains slashes), and compile them into separate regular expressions (`simple_wildcard_regex` and `compound_wildcard_regex`). Only apply the simple regex when iterating over individual parts, and apply the compound regex when accumulating the directory prefix. This optimization prevents unnecessary regex checks in the hot path.

## 2026-05-03 — Exact Ignores Split Optimization

Learning:
Evaluating a combined `exact_ignores` set that includes both simple patterns (e.g. `node_modules`) and compound patterns (e.g. `src/build`) against individual path segments (`parts`) is computationally redundant. A simple pattern correctly evaluates against a single part, but a compound pattern will never match a single segment.

Action:
Split `exact_ignores` into `simple_exact_ignores` (no slashes) and `compound_exact_ignores` (contains slashes), and convert them to `frozenset`s. Only apply the simple ignores when checking `isdisjoint(parts)`, and apply the compound ignores when accumulating the directory prefix. This mirrors the wildcard split optimization and further reduces hashing latency in the hot path.

## 2026-05-12 — Event Handler Lock Contention

Learning:
Acquiring a thread lock (`self.timer_lock`) on every file system event just to update simple state variables (`last_event_time`, `last_event_path`) and spawn a thread creates unnecessary lock contention in high-frequency event loops. Checking `is_shutting_down` via `getattr` is also slightly slower than direct attribute access.

Action:
Prefer direct attribute access for guaranteed attributes (`self.is_shutting_down`). Use double-checked locking when spawning background threads (`if thread is None: with lock: if thread is None: start_thread()`) to avoid acquiring locks on every event, and update thread-safe variables like `time.monotonic()` outside the lock.
## 2026-05-14 — Avoid getattr and redundant evaluations in hot paths

Learning:
Inside the file watcher's `watchdog` event handler, `getattr(event, 'event_type', '')` and `getattr(event, 'src_path', None)` introduce unnecessary `getattr` function call overhead when `event_type` and `src_path` are guaranteed to be present on all watchdog events. Additionally, computing `len(self._abs_base_path)` on every match, checking `if match:` on every iteration before evaluating the regex, and using `self.current_process is process` guards around subprocess return codes introduce latency and bugs.

Action:
Prefer direct attribute access (`event.event_type`, `event.src_path`) over `getattr`. Pre-compute prefix lengths during class initialization. Hoist loop-invariant method lookups (`match = regex.match`) outside of iterations. Remove `self.current_process is process` guards when evaluating subprocess wait results, as the reference can be overwritten during a rapid reload.

## 2026-05-16 — Generator Expression Overhead in Hot Paths

Learning:
In high-frequency Python hot paths (like checking path parts against a regex), using `any()` with a generator expression (e.g., `any(match(p) for p in parts)`) introduces generator overhead that makes it slower than a simple, explicit `for` loop. Additionally, redundant property accesses (`getattr`) and redundant loop-invariant truthiness checks (`if self.compound_wildcard_regex:`) inside loops cause measurable performance regressions.

Action:
Prefer explicit `for` loops with early returns over `any()` generators in hot paths. Lift loop-invariant checks and expensive builtins (like `len()`) outside of tight loops. Use direct attribute access over `getattr` when the attribute's existence is guaranteed.

## 2026-05-20 — Generator Expression Overhead in Object Initialization

Learning:
Using `any()` with a generator expression inside a list comprehension (e.g., `[p for p in patterns if not any(c in p for c in ('*', '?', '['))]`) creates significant generator evaluation overhead, which is magnified when iterating over items. While this was previously addressed in the hot path, it remained in the object initialization, causing minor startup latency.

Action:
Prefer explicit logical string conditions (`if '*' not in p and '?' not in p and '[' not in p`) over `any()` generator expressions for simple string character checks to avoid generator creation overhead, even outside of hot paths.

## 2026-05-27 — Graceful Shutdown Sequence Reliability

Learning:
When implementing graceful shutdown sequences (e.g., `SIGTERM` signal handlers and `KeyboardInterrupt` exception blocks), grouping multiple cleanup steps (like stopping observers, printing output, and shutting down event handlers) into a single try block, or no try block, is unreliable. If an exception occurs in the first step, subsequent critical cleanup steps (like terminating subprocesses) will be silently skipped, leading to orphaned processes and resource leaks.

Action:
Wrap each individual cleanup operation in its own dedicated `try...except Exception: pass` block to guarantee that the failure of one cleanup step does not prevent the execution of the others.

## 2026-05-27 — Loop-Invariant Truthiness Check Overhead

Learning:
Inside the file watcher's `_is_ignored_impl` hot loop, evaluating instance properties like `self.simple_wildcard_regex` repeatedly inside loop conditions (even if implicit truthiness checks) incurs measurable overhead in high-frequency event streams.

Action:
Hoist loop-invariant instance property lookups into local scope variables (`simple_regex = self.simple_wildcard_regex`) outside of loops to prevent redundant evaluation overhead.
