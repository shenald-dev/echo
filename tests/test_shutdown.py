from echo.watcher import CommandRunnerHandler
from unittest.mock import MagicMock

def test_shutdown_prevents_execution():
    handler = CommandRunnerHandler("sleep 10")

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"

    # Trigger event
    handler.on_any_event(mock_event)

    # Capture thread reference before shutdown
    thread = handler.debounce_thread

    # Simulate shutdown
    handler.shutdown()

    # Wait for debounce thread to finish via event instantly instead of sleep
    if thread:
        thread.join(timeout=2.0)

    assert handler.current_process is None or handler.current_process.poll() is not None
