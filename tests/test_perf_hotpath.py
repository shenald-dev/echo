import time
import pytest
from echo.watcher import CommandRunnerHandler

def test_hotpath_performance(benchmark):
    handler = CommandRunnerHandler("echo test", base_path=".")

    # Pre-warm the cache
    handler._is_ignored("build/test.txt")

    # We want to measure the performance of a highly compound path that should *not* match anything
    test_path = "src/very/long/and/deep/path/that/requires/evaluating/multiple/parts/test.py"

    # Function to test
    def run_ignore_check():
        return handler._is_ignored(test_path)

    # First assert correctness
    assert not run_ignore_check()

    # Then benchmark
    benchmark(run_ignore_check)
