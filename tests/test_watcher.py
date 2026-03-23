import time
import subprocess
import threading
import pytest
from unittest.mock import MagicMock, patch
from echo.watcher import CommandRunnerHandler

def test_smart_reload():
    handler = CommandRunnerHandler("sleep 2")

    # Trigger first run
    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"

    handler.on_any_event(mock_event)

    # Should start a process
    time.sleep(0.5)
    first_process = handler.current_process
    assert first_process is not None
    assert first_process.poll() is None  # Still running

    # Trigger second run
    handler.on_any_event(mock_event)

    time.sleep(0.5)
    second_process = handler.current_process
    assert second_process is not first_process

    # First should be terminated
    assert first_process.poll() is not None

    # Second should be running
    assert second_process.poll() is None

    # Cleanup
    second_process.terminate()
    second_process.wait()
