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
        Eager evaluation inside `watchdog` hot paths (like `on_any_event`) causes redundant cache lookups 

        // ... 16864.6 characters truncated (middle section) ...

        `self.is_posix` conditional blocks). However, sleep-based debouncing tests were brittle.

        Action:
        Ensure testing durations account for scheduling overhead but avoid massive overall CI slowdowns.

        2024-04-16 — Trailing Slashes in Ignore Patterns
        Learning: Directory ignore patterns supplied with trailing slashes (e.g., `build/`) fail to match because internal paths are normalized without them.
        Action: Ensure `ignore_patterns` list comprehensions strip trailing slashes (`.rstrip('/')`) alongside other normalizations to guarantee robust matching.

        ## 2026-04-17 — Eager Evaluation & Intent Flag Placement

        Learning:
        Eager evaluation inside `watchdog` hot paths (like `on_any_event`) causes redundant cache lookups 

        // ... 16660.6 characters truncated (middle section) ...

         pass` block to guarantee that the failure of one cleanup step does not prevent the execution of the others.

        ## 2026-05-27 — Loop-Invariant Truthiness Check Overhead

        Learning:
        Inside the file watcher's `_is_ignored_impl` hot loop, evaluating instance properties like `self.simple_wildcard_regex` repeatedly inside loop conditions (even if implicit truthiness checks) incurs measurable overhead in high-frequency event streams.

        Action:
        Hoist loop-invariant instance property lookups into local scope variables (`simple_regex = self.simple_wildcard_regex`) outside of loops to prevent redundant evaluation overhead.