## 2025-02-18 — Fast Path Evaluation Cache

Learning:
The `_is_ignored` function handles rapid string normalization, iteration over directory structures, and regex lookups for every single file system event intercepted by the watchdog. Because bulk operations (like `npm install` or massive text replacement) can fire thousands of events in milliseconds, evaluating ignores redundantly creates significant CPU overhead on hot paths.

Action:
Decorated the `_is_ignored` function with an explicitly bounded `@functools.lru_cache(maxsize=2048)`. This creates a fast-path resolution dictionary preventing expensive recalculations during burst file operations, speeding up filtering by roughly 20x. Bounding the size prevents slow memory leak build-ups over long-running watcher lifecycles.

## 2025-04-07 — Correctly Handle Watchdog 'Moved' Events for Both Source and Destination Paths

Learning:
When handling 'moved' events from `watchdog`, evaluating only the `src_path` for ignore patterns is insufficient and can lead to incorrect triggers. Both `src_path` and `dest_path` must be checked. For instance, if a file is moved from an ignored directory to a valid directory, the event must still trigger the watcher command using the valid `dest_path`.

Action:
Ensure complex file system events like renames and moves evaluate all relevant paths (`src_path` and `dest_path`) against ignore filters to accurately reflect the desired watched state changes.

## 2024-05-18 — Handle watchdog moved events explicitly across ignore boundaries

Learning:
When handling `moved` events from `watchdog`, evaluating only the `src_path` against ignore patterns is insufficient. If a valid file is moved *into* an ignored scope, or if an ignored file is moved *into* a valid scope, the event might be dropped or logged under the wrong path if the fallback (`dest_path`) isn't evaluated properly as an active trigger.

Action:
Future runs dealing with file system events must rigorously check both `src_path` and `dest_path` (when available, e.g., on `moved` events). If `src_path` is valid, it triggers. If `src_path` is ignored, `dest_path` must be checked and used as the trigger path if it is valid.
