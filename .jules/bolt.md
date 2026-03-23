## 2024-05-24 — File watcher thread starvation via shared locks

Learning:
Using a single `threading.Lock()` to synchronize both short-lived operations (like debouncing timers in a file system event callback) and potentially long-running operations (like `process.wait()` on a subprocess) can cause thread starvation. When a slow-terminating subprocess held the lock, the main `watchdog` event loop was blocked, preventing the system from observing new file changes.

Action:
Always use dedicated, fine-grained locks for independent resources. In background-threaded architectures, ensure that event loops are never blocked by slow I/O or process management by separating their locking contexts.
