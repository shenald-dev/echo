# Changelog
## [0.1.27] - 2026-05-14

### Changed
* **[Performance]:** Optimized hot path string slicing in `_is_ignored_impl` by pre-computing string lengths and optimized property access in `on_any_event` by replacing `getattr` with direct property access.

## [0.1.26] - 2026-05-13

### Changed
* **[Performance]:** Optimized event loop lock contention by implementing double-checked locking for debounce thread spawning and moving non-critical state assignments outside the thread lock, reducing overhead in high-frequency event loops.

## [0.1.25] - 2026-05-08

### Changed
* **[Performance]:** Split `exact_ignores` into simple and compound frozensets to prevent redundant exact match evaluations against path segments, mirroring the wildcard optimization and further reducing latency in the hot path.

## [0.1.24] - 2026-05-02

### Changed
* **[Performance]:** Split wildcard ignore patterns into simple and compound regexes to prevent redundant evaluations during path checking, improving file event performance.


## [0.1.23] - 2026-04-30

### Changed
* **[Performance]:** Optimized ignore file filtering in hot paths by fast-tracking common relative paths and avoiding compound loop iterations when unnecessary, significantly reducing CPU cycles on burst saves.

## [0.1.22] - 2026-04-29

### Changed
* **[Reliability]:** Added a SIGTERM signal handler to ensure proper cleanup of subprocesses during graceful shutdowns initiated by containers and process managers.

## [0.1.21] - 2026-04-28

### Changed
* **[Performance]:** Optimized the file event hot path by pre-computing directory prefixes to use fast string slicing instead of `os.path.relpath`.
* **[Reliability]:** Removed blanket `.removeprefix('./')` calls on event paths to prevent unexpected path resolution regressions.

## [0.1.20] - 2026-04-27

### Changed
* **[Reliability]:** Fixed a bug where `rich` would crash with a `MarkupError` if user-provided strings (like exceptions or filenames) contained unescaped markup tags like `[bracket]`.

## [0.1.19] - 2026-04-26

### Changed
* **[Reliability]:** Optimized test suite stability by replacing arbitrary static `time.sleep()` calls with dynamic polling, resolving flakiness when evaluating intermediate process states.

## [0.1.18] - 2026-04-24

### Changed
* **[Lifecycle]:** Assured the optimization of the hot path ignore checks.


## [0.1.17] - 2026-04-23

### Changed
* **[Lifecycle]:** Assured the hot-path ignore logic optimization.

## [0.1.16] - 2026-04-22

### Changed
* **[Performance]:** Eliminated redundant top-level evaluations of exact ignores and wildcards in the file watcher's hot path, reducing evaluation overhead by relying on the iterative path splitting logic.

## [0.1.15] - 2026-04-21

### Changed
* **[Bugfix]:** Fixed an off-by-one bug in the ignore logic to ensure the full multi-part path is evaluated against exact ignore patterns.

## [0.1.14] - 2026-04-20

### Changed
* **[Performance]:** Optimized file event path normalization in the watchdog hot path by replacing `os.path.relpath` with pre-computed fast string slicing. This significantly reduces CPU overhead during high-volume filesystem events.


## [0.1.13] - 2026-04-19

### Changed
* **[Performance]:** Optimized the file event hot path by eliminating redundant cumulative prefix evaluation for directory ignores, marginally decreasing CPU usage for deeply nested paths.

## [0.1.12] - 2026-04-19

### Changed
* **[Reliability]:** Assured the fix for process completion logging. Removed the identity check that caused silent reloads. Assured tests pass.

## [0.1.9] - 2026-04-10

### Changed
* **[Bugfix]:** Fixed an issue where the initial directory prefix was not evaluated against ignore rules, ensuring top-level directories are correctly ignored.
* **[Reliability]:** Added intent flags to correctly process expected exit codes on Windows to avoid misattributing expected graceful process reloading as an execution failure.

## [0.1.8] - 2026-04-09

### Changed
* **[Performance]:** Eliminated artificial shutdown latency by replacing blocking `time.sleep()` with thread-safe `threading.Event().wait()` in the debounce background worker, resulting in instant teardown on termination signals.
* **[Bugfix]:** Fixed an issue where `watchdog` moved events were not properly evaluating the destination path against ignore patterns, ensuring correctly triggered commands when files are moved into a watched scope.

## [0.1.7] - 2026-04-05

### Changed
* **[Performance]:** Bounded LRU cache directly to watcher instances to dramatically accelerate rapid path matching during burst operations while preventing cross-instance memory leaks.

## [0.1.6] - 2026-04-02

### Changed
* **[Reliability]:** Bound LRU caching directly to the watcher instance to prevent cross-instance memory leaks when rapidly re-instantiating.
* **[Reliability]:** Enforced strict relative path evaluation via `os.path.relpath` for complex filter evaluations.

## [0.1.5] - 2026-04-02

### Changed
* **[Bugfix]:** Fixed a regression in path ignore filtering where complex wildcard patterns (e.g., `src/*.tmp`) failed to match correctly. Normalization and full-path evaluation ensures strict isolation of monitored directories.

## [0.1.4] - 2026-04-01

### Changed
* **[Reliability]:** Migrated internal time tracking from `time.time()` to `time.monotonic()` to ensure debouncing stability against system clock shifts and NTP syncs.
* **[Maintenance]:** Pruned unused dependencies and imports from the testing suite to reduce overall entropy.
* **[Documentation]:** Synced README to reflect the stable time tracking behavior.

## [0.1.3] - 2026-03-31

### Changed
* **[Reliability]:** Replaced `time.time()` with `time.monotonic()` in the file watcher and test suites for precise, stable tracking of relative time intervals, debouncing windows, and timeouts. This eliminates vulnerabilities caused by system clock adjustments.
* **[Maintenance]:** Pruned unused module imports from test files to minimize codebase entropy.

## [0.1.1] - 2025-02-21

### Changed
* **[Reliability]:** Implemented a timeout for process termination during file change events and graceful shutdowns. Echo now escalates to forceful termination (`SIGKILL`) to prevent thread deadlocks and application starvation if processes ignore standard termination signals (`SIGTERM`).

## [0.1.2] - 2026-03-27

### Changed
* **[Maintenance]:** Removed unused `test_dir` leftover from previous development cycles.

## [0.1.10] - 2024-04-16

* **Fix:** Normalize ignore patterns by stripping trailing slashes (e.g., `build/` becomes `build`), preventing bugs where valid directory ignore rules failed to match.

## [0.1.11] - 2026-04-17

### Changed
* **[Performance]:** Optimized `on_any_event` by lazy-evaluating destination paths during moved events, saving redundant ignore checks.
* **[Reliability]:** Hardened termination logic to set intent flags *before* making OS-level termination calls, preventing false failure logs when processes end concurrently.
