import timeit
from echo.watcher import CommandRunnerHandler

def test_hotpath_perf():
    handler = CommandRunnerHandler("echo test", base_path=".", ignore_patterns=[".git", "node_modules"])
    paths = ["src/echo/watcher.py", "node_modules/index.js", ".git/HEAD", "tests/test_perf.py"]

    # Run the hot path function 10000 times to simulate burst saves
    start_time = timeit.default_timer()
    for _ in range(10000):
        for path in paths:
            handler._is_ignored(path)
    end_time = timeit.default_timer()

    # Simple assertion to ensure it runs without error and finishes quickly
    duration = end_time - start_time
    assert duration < 1.0  # Should be very fast
    print(f"\nHot path 10k iterations took: {duration:.4f}s")
