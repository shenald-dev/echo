# Changelog

<<<<<<< HEAD
## [0.1.6] - 2026-04-03

### Changed
* **[Reliability]:** Added base path tracking and `os.path.relpath` resolution to the ignore filtering mechanism to correctly apply patterns when `watchdog` surfaces absolute file paths.
=======
## [0.1.6] - 2026-04-02

### Changed
>>>>>>> origin/main
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
