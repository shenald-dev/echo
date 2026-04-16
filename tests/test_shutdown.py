import time
from echo.watcher import CommandRunnerHandler
from unittest.mock import MagicMock

def test_shutdown_prevents_execution():
    handler = CommandRunnerHandler("sleep 10")

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"

    # Trigger event
    handler.on_any_event(mock_event)

    # Wait a bit, but less than debounce threshold (0.25)
    time.sleep(0.1)

    # Simulate shutdown
    handler.shutdown()

    # Wait for debounce thread to finish
    # Sleep interval is 0.5s to comfortably clear the 0.25s debounce window and avoid flaky CI behavior.
    time.sleep(0.5)

    assert handler.current_process is None or handler.current_process.poll() is not None
