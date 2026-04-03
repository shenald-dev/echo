## 2025-02-18 — Fast Path Evaluation Cache

Learning:
The `_is_ignored` function handles rapid string normalization, iteration over directory structures, and regex lookups for every single file system event intercepted by the watchdog. Because bulk operations (like `npm install` or massive text replacement) can fire thousands of events in milliseconds, evaluating ignores redundantly creates significant CPU overhead on hot paths.

Action:
Decorated the `_is_ignored` function with an explicitly bounded `@functools.lru_cache(maxsize=2048)`. This creates a fast-path resolution dictionary preventing expensive recalculations during burst file operations, speeding up filtering by roughly 20x. Bounding the size prevents slow memory leak build-ups over long-running watcher lifecycles.
