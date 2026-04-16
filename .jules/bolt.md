## 2026-04-16 — Watcher Process Termination Logic

Learning:
The POSIX signal checking (`process.returncode == -15`) masked legitimate user command crashes. We can safely remove it in favor of checking the `_echo_terminated` flag because the `_terminate_process` method explicitly sets this attribute on the process object *before* it returns or escalates, regardless of platform (`self.is_posix` conditional blocks). However, sleep-based debouncing tests were brittle.

Action:
Ensure testing durations account for scheduling overhead but avoid massive overall CI slowdowns.

2024-04-16 — Trailing Slashes in Ignore Patterns
Learning: Directory ignore patterns supplied with trailing slashes (e.g., `build/`) fail to match because internal paths are normalized without them.
Action: Ensure `ignore_patterns` list comprehensions strip trailing slashes (`.rstrip('/')`) alongside other normalizations to guarantee robust matching.
