## 2026-04-16 — Watcher Process Termination Logic

Learning:
The POSIX signal checking (`process.returncode == -15`) masked legitimate user command crashes. We can safely remove it in favor of checking the `_echo_terminated` flag because the `_terminate_process` method explicitly sets this attribute on the process object *before* it returns or escal

// ... 16422.8 characters truncated (middle section) ...

previously addressed in the hot path, it remained in the object initialization, causing minor startup latency.

Action:
Prefer explicit logical string conditions (`if '*' not in p and '?' not in p and '[' not in p`) over `any()` generator expressions for simple string character checks to avoid generator creation overhead, even outside of hot paths.