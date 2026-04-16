## 2026-04-16 — Watcher Process Termination Logic

Learning:
The POSIX signal checking (`process.returncode == -15`) masked legitimate user command crashes. We can safely remove it in favor of checking the `_echo_terminated` flag because the `_terminate_process` method explicitly sets this attribute on the process object *before* it returns or escalates, regardless of platform (`self.is_posix` conditional blocks). However, sleep-based debouncing tests were brittle.

Action:
Ensure testing durations account for scheduling overhead but avoid massive overall CI slowdowns.

## 2026-04-10 — Process tracking logic

Learning:
When managing a process state and tracking graceful reloads using flags, assigning the flag after terminating a process in python `subprocess` wrappers opens the state up to being incorrectly reported as crashed. In the file watcher, setting `_echo_terminated` must happen prior to OS signaling.
In addition, watchdog's 'moved' event does not implicitly handle paths. If either the src_path or dest_path fails an ignore check, you can prematurely prevent a process restart for the correct non-ignored path if the other fails.

Action:
Ensure complex file system events accurately evaluate dest and src paths individually, avoiding blanket false checks based on short-circuiting logic. Set intentionality flags like `_echo_terminated` on child processes BEFORE `os.killpg` or `terminate` calls so `OSError` catch blocks do not skip assignment.
