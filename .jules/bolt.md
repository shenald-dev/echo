## 2026-04-16 — Watcher Process Termination Logic

Learning:
The POSIX signal checking (`process.returncode == -15`) masked legitimate user command crashes. We can safely remove it in favor of checking the `_echo_terminated` flag because the `_terminate_process` method explicitly sets this attribute on the process object *before* it returns or escalates, regardless of platform (`self.is_posix` conditional blocks). However, sleep-based debouncing tests were brittle.

Action:
Ensure testing durations account for scheduling overhead but avoid massive overall CI slowdowns.

2024-04-16 — Trailing Slashes in Ignore Patterns
Learning: Directory ignore patterns supplied with trailing slashes (e.g., `build/`) fail to match because internal paths are normalized without them.
Action: Ensure `ignore_patterns` list comprehensions strip trailing slashes (`.rstrip('/')`) alongside other normalizations to guarantee robust matching.

## 2026-04-17 — Eager Evaluation & Intent Flag Placement

Learning:
Eager evaluation inside `watchdog` hot paths (like `on_any_event`) causes redundant cache lookups and array iterations. Specifically, evaluating `_is_ignored(dest_path)` before checking if `src_path` is ignored costs CPU time for every valid "moved" file event. Also, placing intent flags (like `setattr(process, '_echo_terminated', True)`) *after* the OS termination call is unsafe: if the process exits right before termination and throws `OSError`, the intent flag is never set.

Action:
Always lazy-evaluate expensive filters in event-loop hot paths. Always set intent flags *before* executing fallible OS-level state changes to guarantee accurate state tracking in exception handlers.

## 2026-04-17 — Dead Code in Reload Termination Feedback

Learning:
When managing subprocesses, if a reload starts a new process, the class attribute `self.current_process` is reassigned immediately. Therefore, in the wait block of the *old* process, checking `self.current_process is process` will evaluate to `False`. This renders any termination reporting logic nested within that block as dead code, leading to silent reloads.

Action:
Evaluate termination flags (`_echo_terminated`) independently of the "current process" identity check to ensure the correct system feedback is provided regardless of race conditions during reassignment.
