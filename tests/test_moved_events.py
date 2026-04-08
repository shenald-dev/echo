import time
from unittest.mock import MagicMock
from echo.watcher import CommandRunnerHandler

def test_moved_event_triggers_with_dest_path():
    handler = CommandRunnerHandler("echo 1", ignore_patterns=["*.tmp"])

    # Mock 'moved' event where src is ignored but dest is valid
    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.event_type = 'moved'
    mock_event.src_path = "ignored.tmp"
    mock_event.dest_path = "valid.py"

    handler.on_any_event(mock_event)

    time.sleep(0.35)

    assert handler.last_event_path == "valid.py"

    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()

def test_moved_event_triggers_with_src_path_when_dest_ignored():
    handler = CommandRunnerHandler("echo 1", ignore_patterns=["*.tmp"])

    # Mock 'moved' event where src is valid but dest is ignored
    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.event_type = 'moved'
    mock_event.src_path = "valid.py"
    mock_event.dest_path = "ignored.tmp"

    handler.on_any_event(mock_event)

    time.sleep(0.35)

    assert handler.last_event_path == "valid.py"

    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()
