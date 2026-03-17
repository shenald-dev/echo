## 2024-03-17 — Smart Reload Process Management

Learning:
Synchronous file watchers block on long-running commands, leading to queued executions or unresponsive watchers when rapid successive changes occur. Simple debouncing is insufficient for commands that outlive the debounce window.

Action:
Implemented a threaded execution model with a `threading.Lock()` to manage a single `current_process`. Subsequent file changes now intelligently terminate the running process before spawning the new one. This drastically improves responsiveness and eliminates redundant compute overhead during rapid development iterations.
