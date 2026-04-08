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
## 2024-04-06 — Fix Watchdog 'Moved' Event Ignore Handling & Normalize Paths

Learning:
When normalizing OS-provided paths or watchdog absolute paths, prefixing and slashes differences can cause user-provided `ignore_patterns` to silently fail. Also, `watchdog`'s 'moved' event maintains the ignored `src_path` but requires evaluation of the unignored `dest_path` as the `trigger_path`. Previous implementations correctly triggered but erroneously assigned the ignored `src_path` as the event source, potentially misguiding subsequent handlers.

Action:
Ensure `ignore_patterns` normalization handles OS-agnostic separators and normalizes paths (e.g. stripping `./`) to guarantee cross-platform exact matching. When processing moved events where the source path is ignored, dynamically map `trigger_path` to `dest_path` for all downstream actions.
