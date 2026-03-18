## 2024-03-18 — Process Group Termination

Learning:
When using `subprocess.Popen(..., shell=True)`, terminating the process directly (e.g. `process.terminate()`) only kills the top-level shell, leaving child processes (such as the actual command being run) orphaned and still running. This is a significant source of resource leaks and locked ports in a file watcher.

Action:
On POSIX systems, `start_new_session=True` should be passed to `Popen`, and `os.killpg(os.getpgid(pid), signal.SIGTERM)` should be used to terminate the entire process group cleanly. Always double check subprocess termination logic.
