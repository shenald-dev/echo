## 2024-05-24 — File watcher thread starvation via shared locks

Learning:
Using a single `threading.Lock()` to synchronize both short-lived operations (like debouncing timers in a file system event callback) and potentially long-running operations (like `process.wait()` on a subprocess) can cause thread starvation. When a slow-terminating subprocess held the lock, the main `watchdog` event loop was blocked, preventing the system from observing new file changes.

Action:
Always use dedicated, fine-grained locks for independent resources. In background-threaded architectures, ensure that event loops are never blocked by slow I/O or process management by separating their locking contexts.

## 2024-03-24 — Expensive Timer Overhead in Watchdog Events

Learning:
Spawning and cancelling `threading.Timer` inside a lock for every single file system event in Python creates a severe performance and memory churn bottleneck (taking ~0.3s for 1000 burst events).

Action:
Debounce rapid burst events using a single long-lived thread that sleeps until a `last_event_time` threshold is met, rather than starting and stopping threads on every event. This reduces overhead to O(1) time and space.

## 2025-02-21 — Ignoring Read-Only Events in Watchdog

Learning:
The `watchdog` library triggers redundant events on read-only operations like `opened` and `closed_no_write` (e.g., when running `cat` or IDE indexing). Failing to ignore these events results in unnecessary command executions and performance overhead.

Action:
Always explicitly check for and ignore `opened` and `closed_no_write` events (using `getattr(event, 'event_type', '')` for safety) in `watchdog` file system event handlers.
