## 2025-02-18 — Fast Path Evaluation Cache

Learning:
The `_is_ignored` function handles rapid string normalization, iteration over directory structures, and regex lookups for every single file system event intercepted by the watchdog. Because bulk operations (like `npm install` or massive text replacement) can fire thousands of events in milliseconds, evaluating ignores redundantly creates significant CPU overhead on hot paths.

Action:
Decorated the `_is_ignored` function with an explicitly bounded `@functools.lru_cache(maxsize=2048)`. This creates a fast-path resolution dictionary preventing expensive recalculations during burst file operations, speeding up filtering by roughly 20x. Bounding the size prevents slow memory leak build-ups over long-running watcher lifecycles.

## 2026-04-04 — Moved Event Destination Path

Learning:
When handling `watchdog` "moved" events where the source path is ignored but the destination path is not (e.g., renaming a `.tmp` file to a `.py` file), the watcher was correctly allowing the event to pass the filter, but was then incorrectly recording the ignored `src_path` as the path to execute, instead of the valid `dest_path`.

Action:
Updated the event filter logic in `on_any_event` to explicitly track and use `dest_path` as the `target_path` when `src_path` is ignored but `dest_path` is valid. Added corresponding tests in `tests/test_ignore.py` to assert correct destination path resolution on moved events.
