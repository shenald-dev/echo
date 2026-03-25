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

def test_on_any_event_non_blocking():
    """Verify that on_any_event doesn't block while a process is terminating."""
    # A command that takes some time to exit
    handler = CommandRunnerHandler("trap '' TERM; sleep 2")

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"

    # Trigger first run
    handler.on_any_event(mock_event)

    # Wait for the first command to actually start
    time.sleep(0.5)

    # Trigger a second run. This spawns a timer that will try to terminate the first command
    handler.on_any_event(mock_event)

    # Give the thread a little time to start and block in wait()
    time.sleep(0.3)

    start_time = time.time()

    # Trigger third run. This should not block because we're using a separate timer lock
    handler.on_any_event(mock_event)

    elapsed = time.time() - start_time
    assert elapsed < 0.5, f"Watchdog event thread was blocked for {elapsed} seconds!"

    # Cleanup
    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()

def test_ignore_read_only_events():
    handler = CommandRunnerHandler("echo test")

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"
    mock_event.event_type = "opened"

    handler.on_any_event(mock_event)

    assert handler.debounce_thread is None

    mock_event.event_type = "closed_no_write"
    handler.on_any_event(mock_event)

    assert handler.debounce_thread is None

    mock_event.event_type = "modified"
    handler.on_any_event(mock_event)

    assert handler.debounce_thread is not None

    time.sleep(0.5)

    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()
