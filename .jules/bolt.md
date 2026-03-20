## 2024-03-18 — Process Group Termination

Learning:
When using `subprocess.Popen(..., shell=True)`, terminating the process directly (e.g. `process.terminate()`) only kills the top-level shell, leaving child processes (such as the actual command being run) orphaned and still running. This is a significant source of resource leaks and locked ports in a file watcher.

Action:
On POSIX systems, `start_new_session=True` should be passed to `Popen`, and `os.killpg(os.getpgid(pid), signal.SIGTERM)` should be used to terminate the entire process group cleanly. Always double check subprocess termination logic.

## 2024-05-28 — File watcher debounce implementation

Learning:
The previous `time.time() - last_run` debounce implementation was flawed because it reset `last_run` only after a command completed execution, causing subsequent events that happened during execution or immediately after to be completely ignored. This broke the core "smart reload" feature where new changes should terminate the running process.

Action:
Replaced the manual time-tracking debounce with a trailing-edge `threading.Timer(0.25)` implementation. The timer is reset on every incoming event, ensuring the command executes exactly once, 0.25 seconds after a burst of file operations has settled, properly terminating any previous commands if they were still running.
