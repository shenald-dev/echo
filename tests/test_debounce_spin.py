import time
import threading
from echo.watcher import CommandRunnerHandler
from unittest.mock import MagicMock

def test_debounce_none_event_does_not_spin():
    handler = CommandRunnerHandler("echo test")

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = ""
    mock_event.event_type = "modified"

    handler.on_any_event(mock_event)

    # Event path is empty, so the thread should not even start
    assert handler.debounce_thread is None

def test_debounce_thread_terminates():
    handler = CommandRunnerHandler("echo test")

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "valid.txt"
    mock_event.event_type = "modified"

    handler.on_any_event(mock_event)
    assert handler.debounce_thread is not None

    # Wait for the thread to reach timeout
    time.sleep(0.5)

    # Check that thread exited cleanly
    assert handler.debounce_thread is None

    # Ensure no zombie thread is spinning
    for t in threading.enumerate():
        assert "debounce" not in t.name.lower() or not t.is_alive()
