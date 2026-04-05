import time
from unittest.mock import MagicMock
from echo.watcher import CommandRunnerHandler

def test_moved_event_with_ignored_src():
    handler = CommandRunnerHandler("echo 1", ignore_patterns=["*.tmp"])

    # Mock 'moved' event from ignored src to valid dest
    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.event_type = 'moved'
    mock_event.src_path = "ignored.tmp"
    mock_event.dest_path = "valid.py"

    handler.on_any_event(mock_event)

    time.sleep(0.35)

    # Process should start
    assert handler.current_process is not None
    # And the recorded path should be the valid dest_path
    assert handler.last_event_path == "valid.py"

    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()

def test_moved_event_with_valid_src_and_dest():
    handler = CommandRunnerHandler("echo 1", ignore_patterns=["*.tmp"])

    # Mock 'moved' event from valid src to valid dest
    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.event_type = 'moved'
    mock_event.src_path = "valid1.py"
    mock_event.dest_path = "valid2.py"

    handler.on_any_event(mock_event)

    time.sleep(0.35)

    # Process should start
    assert handler.current_process is not None

    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()
