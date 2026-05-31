import time
from unittest.mock import MagicMock
from echo.watcher import CommandRunnerHandler

def test_is_ignored_exact_match():
    handler = CommandRunnerHandler("echo 1")

    assert handler._is_ignored("node_modules/express/index.js") is True
    assert handler._is_ignored(".git/HEAD") is True
    assert handler._is_ignored("src/echo/__pycache__/watcher.cpython-312.pyc") is True
    assert handler._is_ignored(".pytest_cache/v/cache/nodeids") is True
    assert handler._is_ignored("venv/bin/python") is True
    assert handler._is_ignored(".venv/bin/python") is True

    assert handler._is_ignored("src/echo/watcher.py") is False
    assert handler._is_ignored("my_venv/bin/python") is False
    assert handler._is_ignored("test_node_modules.py") is False

def test_is_ignored_wildcard_match():
    handler = CommandRunnerHandler("echo 1", ignore_patterns=["*.tmp", "build*", "src/*.tmp", "docs/build/*"])

    assert handler._is_ignored("test.tmp") is True
    assert handler._is_ignored("src/build_output/main.js") is True
    assert handler._is_ignored("src/test.tmp") is True
    assert handler._is_ignored("docs/build/index.html") is True
    assert handler._is_ignored("./src/test.tmp") is True
    assert handler._is_ignored("src\\test.tmp") is True

    assert handler._is_ignored("test.txt") is False
    assert handler._is_ignored("docs/index.html") is False

def test_is_ignored_compound_path_match():
    handler = CommandRunnerHandler("echo 1", ignore_patterns=["src/build", "docs/temp", "src/*.tmp"])

    assert handler._is_ignored("src/build/test.txt") is True
    assert handler._is_ignored("docs/temp/index.html") is True
    assert handler._is_ignored("src/my_folder.tmp/test.txt") is True

    assert handler._is_ignored("src/test.txt") is False
    assert handler._is_ignored("docs/index.html") is False

def test_ignored_events_do_not_trigger():
    handler = CommandRunnerHandler("echo 1", ignore_patterns=["*.tmp", "ignored_dir"])

    # Mock event for ignored path
    mock_event_ignored = MagicMock(spec=["is_directory", "event_type", "src_path"])
    mock_event_ignored.is_directory = False
    mock_event_ignored.event_type = 'modified'
    mock_event_ignored.src_path = "test.tmp"

    handler.on_any_event(mock_event_ignored)

    assert handler.debounce_thread is None, "Thread should not be started for ignored event"
    assert handler.current_process is None, "Process should not be started for ignored event"

    # Mock moved event where dest_path is ignored but src_path is valid
    mock_event_moved_dest_ignored = MagicMock(spec=["is_directory", "event_type", "src_path", "dest_path"])
    mock_event_moved_dest_ignored.is_directory = False
    mock_event_moved_dest_ignored.event_type = 'moved'
    mock_event_moved_dest_ignored.src_path = "test.txt"
    mock_event_moved_dest_ignored.dest_path = "test.tmp"

    handler.on_any_event(mock_event_moved_dest_ignored)

    # Wait for the process to start
    start_time = time.monotonic()
    while handler.current_process is None and time.monotonic() - start_time < 3.0:
        time.sleep(0.05)

    assert handler.current_process is not None, "Process should be started if src_path is valid even if dest_path is ignored"

    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()
        handler.current_process = None

    # Mock moved event where src_path is ignored but dest_path is valid
    mock_event_moved_valid_dest = MagicMock(spec=["is_directory", "event_type", "src_path", "dest_path"])
    mock_event_moved_valid_dest.is_directory = False
    mock_event_moved_valid_dest.event_type = 'moved'
    mock_event_moved_valid_dest.src_path = "ignored_dir/file.txt"
    mock_event_moved_valid_dest.dest_path = "valid_dir/file.txt"

    handler.on_any_event(mock_event_moved_valid_dest)

    # Wait for the process to start
    start_time = time.monotonic()
    while handler.current_process is None and time.monotonic() - start_time < 3.0:
        time.sleep(0.05)

    assert handler.current_process is not None, "Process should be started for valid dest_path"
    assert handler.last_event_path == "valid_dir/file.txt", "last_event_path should be updated to dest_path"

    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()
        handler.current_process = None

    # Mock event for valid path
    mock_event_valid = MagicMock(spec=["is_directory", "event_type", "src_path"])
    mock_event_valid.is_directory = False
    mock_event_valid.event_type = 'modified'
    mock_event_valid.src_path = "test.txt"

    handler.on_any_event(mock_event_valid)

    # Wait for the process to start
    start_time = time.monotonic()
    while handler.current_process is None and time.monotonic() - start_time < 3.0:
        time.sleep(0.05)

    assert handler.current_process is not None, "Process should be started for valid event"

    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()

def test_trailing_slashes_in_ignores():
    handler = CommandRunnerHandler("echo 1", ignore_patterns=["build/", "temp\\", "docs//"])

    assert handler._is_ignored("build/index.js") is True, "build/index.js should be ignored"
    assert handler._is_ignored("temp/index.js") is True, "temp/index.js should be ignored"
    assert handler._is_ignored("docs/index.js") is True, "docs/index.js should be ignored"

def test_character_class_wildcard_match():
    handler = CommandRunnerHandler("echo 1", ignore_patterns=["[a-z].tmp"])

    # Must correctly categorize as wildcard and compile regex
    assert handler.simple_wildcard_regex is not None
    assert "[a-z].tmp" not in handler.simple_exact_ignores

    assert handler._is_ignored("a.tmp") is True
    assert handler._is_ignored("z.tmp") is True
    assert handler._is_ignored("1.tmp") is False
    assert handler._is_ignored("A.tmp") is False


def test_is_ignored_abs_base_path_match():
    import os
    from echo.watcher import CommandRunnerHandler
    base = os.path.abspath('.')
    handler = CommandRunnerHandler('echo test', base_path='.', ignore_patterns=['test_dir'])
    # Test abs_base_path startswith
    abs_path = os.path.join(base, 'test_dir', 'file.txt')
    assert handler._is_ignored(abs_path) is True
    # Test exactly abs_base_path without trailing slash
    assert handler._is_ignored(base) is False

def test_is_ignored_performance_benchmark():
    import time, os
    from echo.watcher import CommandRunnerHandler
    base = os.path.abspath('.')
    handler = CommandRunnerHandler('echo test', base_path='.', ignore_patterns=['node_modules', 'build', '*.tmp'])

    # Warm up cache (though we are testing the function logic primarily)
    test_paths = [
        os.path.join(base, 'src', 'app.py'),
        os.path.join(base, 'node_modules', 'pkg', 'index.js'),
        os.path.join(base, 'build', 'output.bin'),
        os.path.join(base, 'src', 'test.tmp')
    ] * 1000

    start = time.monotonic()
    for path in test_paths:
        handler._is_ignored_impl(path)  # Bypass LRU cache to test raw implementation speed
    duration = time.monotonic() - start

    # Assert it takes less than a reasonable threshold (e.g., 0.5s for 4000 calls)
    # In a real hot path we want this to be extremely fast.
    assert duration < 0.5
