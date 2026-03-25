## 2025-03-25 — Watchdog Read-Only Events Over-triggering

Learning:
The `watchdog` library on OS platforms will trigger `opened` and `closed_no_write` events when a file is simply read by another tool or IDE, which caused the watcher to needlessly re-execute the user's command. This creates redundant background work and false positives on "changes."

Action:
Ensure future file watcher logic explicitly ignores `opened` and `closed_no_write` events so it only acts on real modifications (like `modified`, `created`, or `moved`).
