import timeit
import pytest
from echo.watcher import CommandRunnerHandler

def test_performance_is_ignored_hotpath():
    handler = CommandRunnerHandler("echo test", ".", ignore_patterns=["*.tmp", "node_modules", "src/build", "test/*.log"])

    # Initialize LRU cache to make the test measure the internal execution not the cache wrapper
    # We call the underlying un-cached implementation directly to measure the hot path

    def run_miss():
        handler._is_ignored_impl("src/test/abc.py")

    def run_simple_exact():
        handler._is_ignored_impl("node_modules/abc/def.js")

    def run_compound_exact():
        handler._is_ignored_impl("src/build/output.o")

    def run_wildcard():
        handler._is_ignored_impl("test/run.log")

    iterations = 10000

    time_miss = timeit.timeit(run_miss, number=iterations)
    time_simple_exact = timeit.timeit(run_simple_exact, number=iterations)
    time_compound_exact = timeit.timeit(run_compound_exact, number=iterations)
    time_wildcard = timeit.timeit(run_wildcard, number=iterations)

    # Sanity checks: These shouldn't take more than a second even on slow CIs for 10k iterations
    assert time_miss < 1.0, f"Miss path is too slow: {time_miss}"
    assert time_simple_exact < 1.0, f"Simple exact path is too slow: {time_simple_exact}"
    assert time_compound_exact < 1.0, f"Compound exact path is too slow: {time_compound_exact}"
    assert time_wildcard < 1.0, f"Wildcard path is too slow: {time_wildcard}"

def test_performance_on_any_event_lock():
    handler = CommandRunnerHandler("echo test", ".", ignore_patterns=[])

    # Simulate a high-frequency event burst where a debounce is already active
    # This specifically tests that the lock isn't repeatedly acquired

    import threading
    handler.debounce_thread = threading.Thread(target=lambda: None) # mock active thread

    event = type("Event", (), {"is_directory": False, "event_type": "modified", "src_path": "src/test/abc.py", "dest_path": None})()

    def run_events():
        for _ in range(10000):
            handler.on_any_event(event)

    time_events = timeit.timeit(run_events, number=1)

    # 10k lock-free iterations should easily complete within 0.1s
    assert time_events < 0.2, f"Event dispatching overhead is too high: {time_events}"
```