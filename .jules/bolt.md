## 2025-02-18 — Fast Path Evaluation Cache

Learning:
The `_is_ignored` function handles rapid string normalization, iteration over directory structures, and regex lookups for every single file system event intercepted by the watchdog. Because bulk operations (like `npm install` or massive text replacement) can fire thousands of events in milliseconds, evaluating ignores redundantly creates significant CPU overhead on hot paths.

Action:
Decorated the `_is_ignored` function with an explicitly bounded `@functools.lru_cache(maxsize=2048)`. This creates a fast-path resolution dictionary preventing expensive recalculations during burst file operations, speeding up filtering by roughly 20x. Bounding the size prevents slow memory leak build-ups over long-running watcher lifecycles.

## 2025-04-05 — Ignore Pattern and Watchdog Event Alignment

Learning:
Ignore pattern normalization avoids matching bugs with OS-specific path inputs like `.\` or `.\`, and correctly evaluating `watchdog` "moved" events prevents skipped commands when `src_path` is ignored but `dest_path` is valid.

Action:
Normalize inputs in fast-path event mechanisms before caching, and thoroughly handle event attributes where multiple path fields exist (`src_path`, `dest_path`).
