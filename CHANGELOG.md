# Changelog
   ## [0.1.32] - 2026-05-28

## [0.1.33] - 2026-05-31

### Performance
- Optimized `_is_ignored` hot path by replacing expensive `range(1, len(parts))` and `path.replace` operations with explicit slices (`parts[1:]`) and condition checks (`if '\\' in path:`).

### Changed
* **[Lifecycle]:** Assured the hot-path ignore optimizations (eliminating redundant path splitting for root files and deferring `dest_path` extraction). Verified structural soundness and zero dead code.

## [0.1.32] - 2026-05-29

### Performance
- Optimized `_is_ignored` hot path by bypassing `dest_path` extraction and path splitting for common scenarios, reducing overhead during burst file events.

## [0.1.31] - 2026-05-28

### Changed
* **[Quality]:** Assured the optimization to hoist regex variables in the ignore loop. Resolved static analysis warnings related to mocking in the shutdown test suite.
* **[Lifecycle]:** Synced documentation and pruned dead code.


## [0.1.30] - 2026-05-27

### Changed
* **[Performance]:** Hoisted loop-invariant truthiness checks and regex property lookups into local scope within the ignore evaluation hot path to reduce evaluation overhead.

## [0.1.29] - 2026-05-23

### Changed
* **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.

## [0.1.28] - 2026-05-22

   ### Changed
   * **[Reliability]:** Hardened graceful shutdown sequences (`SIGTERM` and `KeyboardInterrupt`) by isolating individual cleanup operations into dedicated exception blocks that log errors instead of silently passing. This preserves debuggability and prevents exceptions during early cleanup phases from

   // ... 8032 characters truncated (middle section) ...

   ## [0.1.11] - 2026-04-17

   ### Changed
   * **[Performance]:** Optimized `on_any_event` by lazy-evaluating destination paths during moved events, saving redundant ignore checks.
   * **[Reliability]:** Hardened termination logic to set intent flags *before* making OS-level termination calls, preventing false failure logs when processes end concurrently.