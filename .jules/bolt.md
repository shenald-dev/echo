## 2026-04-16 — Watcher Process Termination Logic

Learning:
The POSIX signal checking (`process.returncode == -15`) masked legitimate user command crashes. We can safely remove it in favor of checking the `_echo_terminated` flag because the `_terminate_process` method explicitly sets this attribute on the process object *before* it returns or esca

// ... 19271 characters truncated (middle section) ...

side the `on_any_event` handler of the file watcher, properties like `event_type` and `src_path` are guaranteed to exist on watchdog events. Looking them up via `getattr` is slower than direct attribute access.

Action:
Prefer direct attribute access (`event.event_type` and `event.src_path`) over `getattr` when the attribute is guaranteed to exist.