import timeit
from echo.watcher import CommandRunnerHandler

def test_ignore_performance_no_regression():
    handler = CommandRunnerHandler("echo test", ignore_patterns=["node_modules", "*.tmp", "src/build", "docs/temp"])

    deep_path = "src/very/deep/nested/directory/structure/that/has/no/ignores/here/my_file.txt"

    # Run it once to prime any possible setup
    handler._is_ignored_impl(deep_path)

    # Time it for 10,000 iterations to ensure it's sufficiently fast
    start = timeit.default_timer()
    for _ in range(10000):
        handler._is_ignored_impl(deep_path)
    end = timeit.default_timer()

    duration = end - start

    # Our hoisted optimization should easily clear 10k iterations in under 0.5s on any modern hardware.
    # We set a generous upper bound for CI reliability, but this ensures no major regressions happen.
    assert duration < 1.0, f"Performance regression in ignore logic: 10,000 deep paths took {duration:.2f}s (threshold 1.0s)"
