We need to merge two versions of CHANGELOG.md.

Base branch (main) content:

```
# Changelog

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

```

Head branch (jules-1071597030095575902-03e18487) content:

```
## v0.1.9
* **[Reliability]:** Addressed test flakiness under CI bounds and corrected destination evaluation for moved file system events.

# Changelog

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

```

We need to merge all meaningful changes from both branches.

Observations:

- Base has a header "# Changelog" at top, then entries for [0.1.9] - 2026-04-10, then [0.1.8] etc.

- Head branch starts with a line "## v0.1.9" (note: no date) and bullet "* **[Reliability]:** Addressed test flakiness under CI bounds and corrected destination evaluation for moved file system events." Then after that line, it has "# Changelog" and then entries from [0.1.8] downwards identical to base (except maybe some differences? Let's compare.)

The head branch's entries from [0.1.8] onward appear identical to base's entries for those versions (I need to verify each line). Let's compare:

Base [0.1.8] section:

```
## [0.1.8] - 2026-04-09

### Changed
* **[Performance]:** Eliminated artificial shutdown latency by replacing blocking `time.sleep()` with thread-safe `threading.Event().wait()` in the debounce background worker, resulting in instant teardown on termination signals.
* **[Bugfix]:** Fixed an issue where `watchdog` moved events were not properly evaluating the destination path against ignore patterns, ensuring correctly triggered commands when files are moved into a watched scope.
```

Head [0.1.8] section:

```
## [0.1.8] - 2026-04-09

### Changed
* **[Performance]:** Eliminated artificial shutdown latency by replacing blocking `time.sleep()` with thread-safe `threading.Event().wait()` in the debounce background worker, resulting in instant teardown on termination signals.
* **[Bugfix]:** Fixed an issue where `watchdog` moved events were not properly evaluating the destination path against ignore patterns, ensuring correctly triggered commands when files are moved into a watched scope.
```

Identical.

[0.1.7] identical? Base:

```
## [0.1.7] - 2026-04-05

### Changed
* **[Performance]:** Bounded LRU cache directly to watcher instances to dramatically accelerate rapid path matching during burst operations while preventing cross-instance memory leaks.
```

Head:

```
## [0.1.7] - 2026-04-05

### Changed
* **[Performance]:** Bounded LRU cache directly to watcher instances to dramatically accelerate rapid path matching during burst operations while preventing cross-instance memory leaks.
```

Identical.

[0.1.6] identical? Base:

```
## [0.1.6] - 2026-04-02

### Changed
* **[Reliability]:** Bound LRU caching directly to the watcher instance to prevent cross-instance memory leaks when rapidly re-instantiating.
* **[Reliability]:** Enforced strict relative path evaluation via `os.path.relpath` for complex filter evaluations.
```

Head:

```
## [0.1.6] - 2026-04-02

### Changed
* **[Reliability]:** Bound LRU caching directly to the watcher instance to prevent cross-instance memory leaks when rapidly re-instantiating.
* **[Reliability]:** Enforced strict relative path evaluation via `os.path.relpath` for complex filter evaluations.
```

Identical.

[0.1.5] identical? Base:

```
## [0.1.5] - 2026-04-02

### Changed
* **[Bugfix]:** Fixed a regression in path ignore filtering where complex wildcard patterns (e.g., `src/*.tmp`) failed to match correctly. Normalization and full-path evaluation ensures strict isolation of monitored directories.
```

Head:

```
## [0.1.5] - 2026-04-02

### Changed
* **[Bugfix]:** Fixed a regression in path ignore filtering where complex wildcard patterns (e.g., `src/*.tmp`) failed to match correctly. Normalization and full-path evaluation ensures strict isolation of monitored directories.
```

Identical.

[0.1.4] identical? Base:

```
## [0.1.4] - 2026-04-01

### Changed
* **[Reliability]:** Migrated internal time tracking from `time.time()` to `time.monotonic()` to ensure debouncing stability against system clock shifts and NTP syncs.
* **[Maintenance]:** Pruned unused dependencies and imports from the testing suite to reduce overall entropy.
* **[Documentation]:** Synced README to reflect the stable time tracking behavior.
```

Head:

```
## [0.1.4] - 2026-04-01

### Changed
* **[Reliability]:** Migrated internal time tracking from `time.time()` to `time.monotonic()` to ensure debouncing stability against system clock shifts and NTP syncs.
* **[Maintenance]:** Pruned unused dependencies and imports from the testing suite to reduce overall entropy.
* **[Documentation]:** Synced README to reflect the stable time tracking behavior.
```

Identical.

[0.1.3] identical? Base:

```
## [0.1.3] - 2026-03-31

### Changed
* **[Reliability]:** Replaced `time.time()` with `time.monotonic()` in the file watcher and test suites for precise, stable tracking of relative time intervals, debouncing windows, and timeouts. This eliminates vulnerabilities caused by system clock adjustments.
* **[Maintenance]:** Pruned unused module imports from test files to minimize codebase entropy.
```

Head:

```
## [0.1.3] - 2026-03-31

### Changed
* **[Reliability]:** Replaced `time.time()` with `time.monotonic()` in the file watcher and test suites for precise, stable tracking of relative time intervals, debouncing windows, and timeouts. This eliminates vulnerabilities caused by system clock adjustments.
* **[Maintenance]:** Pruned unused module imports from test files to minimize codebase entropy.
```

Identical.

[0.1.1] identical? Base:

```
## [0.1.1] - 2025-02-21

### Changed
* **[Reliability]:** Implemented a timeout for process termination during file change events and graceful shutdowns. Echo now escalates to forceful termination (`SIGKILL`) to prevent thread deadlocks and application starvation if processes ignore standard termination signals (`SIGTERM`).

```

Head:

```
## [0.1.1] - 2025-02-21

### Changed
* **[Reliability]:** Implemented a timeout for process termination during file change events and graceful shutdowns. Echo now escalates to forceful termination (`SIGKILL`) to prevent thread deadlocks and application starvation if processes ignore standard termination signals (`SIGTERM`).

```

Identical.

[0.1.2] identical? Base:

```
## [0.1.2] - 2026-03-27

### Changed
* **[Maintenance]:** Removed unused `test_dir` leftover from previous development cycles.

```

Head:

```
## [0.1.2] - 2026-03-27

### Changed
* **[Maintenance]:** Removed unused `test_dir` leftover from previous development cycles.

```

Identical.

Thus the only differences are:

- Base has a header "# Changelog" at top, then [0.1.9] entry with two bullet points.

- Head has a line "## v0.1.9" with a bullet point about reliability (test flakiness and destination evaluation), then "# Changelog", then the rest same as base (including [0.1.8] etc). Notably, head does NOT have the [0.1.9] entry with date and two bullet points; instead it has a different format for v0.1.9 (no date) and a different bullet.

We need to merge all meaningful changes from both branches. So we need to include both the base's [0.1.9] entry (with date and two bullet points) and the head's v0.1.9 entry (without date, with its bullet). However, note that they both refer to version 0.1.9 but with different formatting and content. We need to combine them logically.

We should keep the header "# Changelog" at top (base has it, head has it after the v0.1.9 line). The merged file should have a single "# Changelog" header.

We need to decide how to represent version 0.1.9. The base uses "[0.1.9] - 2026-04-10". The head uses "## v0.1.9" (no date). Probably we should keep the dated format as it's more standard. The head's entry is about reliability: "Addressed test flakiness under CI bounds and corrected destination evaluation for moved file system events." The base's entry has two bullet points: bugfix about initial directory prefix, and reliability about intent flags for Windows exit codes.

We should combine both sets of changes under the same version heading, preserving both bullet points from base and the bullet from head. However, we must avoid duplication if any bullet is same? They are different.

Thus under version 0.1.9 we could have:

## [0.1.9] - 2026-04-10

### Changed
* **[Bugfix]:** Fixed an issue where the initial directory prefix was not evaluated against ignore rules, ensuring top-level directories are correctly ignored.
* **[Reliability]:** Added intent flags to correctly process expected exit codes on Windows to avoid misattributing expected graceful process reloading as an execution failure.
* **[Reliability]:** Addressed test flakiness under CI bounds and corrected destination evaluation for moved file system events.

But note that the head's bullet is also under Reliability. Could combine or keep separate. It's fine.

Alternatively, we could keep the head's line as a separate entry "## v0.1.9" but that would duplicate version. Better to merge.

Thus final merged file:

Start with "# Changelog"

Then the merged [0.1.9] section as above.

Then the rest of the sections from [0.1.8] down to [0.1.2] as they are identical in both.

We must ensure no extra blank lines incorrectly.

Let's construct.

Base after [0.1.9] had a blank line before next section? In base, after the [0.1.9] section there is a blank line then "## [0.1.8] - 2026-04-09". We'll replicate.

Thus final:

```
# Changelog

## [0.1.9] - 2026-04-10

### Changed
* **[Bugfix]:** Fixed an issue where the initial directory prefix was not evaluated against ignore rules, ensuring top-level directories are correctly ignored.
* **[Reliability]:** Added intent flags to correctly process expected exit codes on Windows to avoid misattributing expected graceful process reloading as an execution failure.
* **[Reliability]:** Addressed test flakiness under CI bounds and corrected destination evaluation for moved file system events.

## [0.1.8] - 2026-04-09

### Changed
* **[Performance]:** Eliminated artificial shutdown latency by replacing blocking `time.sleep()` with thread-safe `threading.Event().wait()` in the debounce background worker, resulting in instant teardown on termination signals.
* **[Bugfix]:** Fixed an issue where `watchdog` moved events were not properly evaluating the destination path against ignore patterns, ensuring correctly triggered commands when files are moved into a watched scope.

## [0.1.7] - 2026-04-05

### Changed
* **[Performance]:** Bounded