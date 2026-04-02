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
    handler = CommandRunnerHandler("echo 1", ignore_patterns=["*.tmp"])

    # Mock event for ignored path
    mock_event_ignored = MagicMock(spec=["is_directory", "event_type", "src_path"])
    mock_event_ignored.is_directory = False
    mock_event_ignored.event_type = 'modified'
    mock_event_ignored.src_path = "test.tmp"

    handler.on_any_event(mock_event_ignored)

    time.sleep(0.35)

    assert handler.current_process is None, "Process should not be started for ignored event"

    # Mock event for valid path
    mock_event_valid = MagicMock(spec=["is_directory", "event_type", "src_path"])
    mock_event_valid.is_directory = False
    mock_event_valid.event_type = 'modified'
    mock_event_valid.src_path = "test.txt"

    handler.on_any_event(mock_event_valid)

    time.sleep(0.35)

    assert handler.current_process is not None, "Process should be started for valid event"

    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()
