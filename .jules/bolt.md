## 2026-04-16 — Watcher Process Termination Logic

Learning:
The POSIX signal checking (`process.returncode == -15`) masked legitimate user command crashes. We can safely remove it in favor of checking the `_echo_terminated` flag because the `_terminate_process` method explicitly sets this attribute on the process object *before* it returns or escalates, regardless of platform (`self.is_posix` conditional blocks). However, sleep-based debouncing tests were brittle.

Action:
Ensure testing durations account for scheduling overhead but avoid massive overall CI slowdowns.

## 2025-04-10 — Refine Subprocess Intent Tracking Logic

Learning:
When forcefully reloading running subprocesses on POSIX systems via `os.killpg()`, an `OSError` may be raised before the `_echo_terminated` intent flag is set, resulting in the termination being misclassified as a crash instead of a planned reload. Furthermore, relying on platform-specific exit codes (like -15 for SIGTERM) to classify intent is brittle and misses edge cases.

Action:
Set the intent flag `getattr(process, '_echo_terminated', False)` immediately *before* calling termination functions to guarantee the intent is correctly recorded, even if an `OSError` interrupts the signal propagation. Update the return code processing block to rely exclusively on this explicit flag across all platforms rather than parsing arbitrary exit codes.
