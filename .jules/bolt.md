## 2025-02-18 — Fast Path Evaluation Cache

Learning:
The `_is_ignored` function handles rapid string normalization, iteration over directory structures, and regex lookups for every single file system event intercepted by the watchdog. Because bulk operations (like `npm install` or massive text replacement) can fire thousands of events in milliseconds, evaluating ignores redundantly creates significant CPU overhead on hot paths.

Action:
Decorated the `_is_ignored` function with an explicitly bounded `@functools.lru_cache(maxsize=2048)`. This creates a fast-path resolution dictionary preventing expensive recalculations during burst file operations, speeding up filtering by roughly 20x. Bounding the size prevents slow memory leak build-ups over long-running watcher lifecycles.

## 2025-04-07 — Correctly Handle Watchdog 'Moved' Events for Both Source and Destination Paths

Learning:
When handling 'moved' events from `watchdog`, evaluating only the `src_path` for ignore patterns is insufficient and can lead to incorrect triggers. Both `src_path` and `dest_path` must be checked. For instance, if a file is moved from an ignored directory to a valid directory, the event must still trigger the watcher command using the valid `dest_path`.

Action:
Ensure complex file system events like renames and moves evaluate all relevant paths (`src_path` and `dest_path`) against ignore filters to accurately reflect the desired watched state changes.

## 2025-04-08 — Optimize Shutdown Latency with threading.Event

Learning:
Using `time.sleep()` inside background daemon threads (like the file watcher's debouncer) blocks the thread unconditionally for the duration of the sleep. During application shutdown, this creates an artificial latency penalty where the application must wait for the sleep to expire before the thread can check the termination flag and exit cleanly.

Action:
Replaced `time.sleep(time_to_wait)` with `self.shutdown_event.wait(timeout=time_to_wait)` in the background debouncer. This allows the thread to still pause for the required debounce interval but unblock instantly when `shutdown()` is called and sets the event, eliminating up to 0.25 seconds of unnecessary blocking on exit.

## 2025-04-09 — Watchdog Ignore Logic & Windows Termination Handling

Learning:
When building cumulative directory prefixes to check against ignore patterns (e.g., looping to construct `a`, `a/b`, `a/b/c`), the initial prefix (`parts[0]`) was bypassing evaluation, causing top-level directory ignore rules to be missed. Additionally, on Windows, process termination typically yields a return code of 1, which was incorrectly parsed as a crash rather than a graceful reload.

Action:
Ensure the first prefix string in an ignore path evaluation is directly verified against exact and wildcard patterns before appending the rest of the path parts. For Windows process management, explicitly attach an intent flag (e.g. `_echo_terminated = True`) before calling `.terminate()` so the exit code 1 can be properly disambiguated from actual failures.
## 2024-05-15 — Test and watcher termination reliability

Learning:
Tests involving the file watcher must account for the 0.25-second trailing-edge debounce window by using a time.sleep() duration comfortably longer than the debounce window (e.g., 0.5 to 1.0 seconds) before asserting process state. Shorter durations (like 0.35s) are prone to flakiness due to CI or thread scheduling overhead, especially when running `pytest-cov`. Additionally, OS-level return code checks for deliberate termination in subprocesses are fragile; tracking intentional termination using an explicit instance attribute (e.g., `_echo_terminated`) is safer.

Action:
Ensure sleep times in future watcher tests are sufficiently long (>=0.5s), and avoid hardcoding OS exit codes for control flow tracking in background process lifecycles.
