# Changelog

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
