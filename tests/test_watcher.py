import time
from unittest.mock import MagicMock
from echo.watcher import CommandRunnerHandler

def test_smart_reload():
    handler = CommandRunnerHandler("sleep 2")

    # Trigger first run
    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"

    handler.on_any_event(mock_event)

    # Should start a process
    # Wait for process to start
    start_time = time.monotonic()
    while handler.current_process is None and time.monotonic() - start_time < 3.0:
        time.sleep(0.05)
    first_process = handler.current_process
    assert first_process is not None
    assert first_process.poll() is None  # Still running

    # Trigger second run
    handler.on_any_event(mock_event)

    # Wait for second process to start
    start_time = time.monotonic()
    while (handler.current_process is None or handler.current_process is first_process) and time.monotonic() - start_time < 3.0:
        time.sleep(0.05)
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
    time.sleep(1.0)

    # Trigger a second run. This spawns a timer that will try to terminate the first command
    handler.on_any_event(mock_event)

    # Give the thread a little time to start and block in wait()
    time.sleep(0.3)

    start_time = time.monotonic()

    # Trigger third run. This should not block because we're using a separate timer lock
    handler.on_any_event(mock_event)

    elapsed = time.monotonic() - start_time
    assert elapsed < 0.5, f"Watchdog event thread was blocked for {elapsed} seconds!"

    # Cleanup
    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()

def test_ignore_read_only_events():
    """Verify that read-only events (opened, closed_no_write) are ignored."""
    handler = CommandRunnerHandler("echo 1")

    # Mock 'opened' event
    mock_event_opened = MagicMock()
    mock_event_opened.is_directory = False
    mock_event_opened.event_type = 'opened'
    mock_event_opened.src_path = "test.py"

    # Mock 'closed_no_write' event
    mock_event_closed = MagicMock()
    mock_event_closed.is_directory = False
    mock_event_closed.event_type = 'closed_no_write'
    mock_event_closed.src_path = "test.py"

    # Trigger events
    handler.on_any_event(mock_event_opened)
    handler.on_any_event(mock_event_closed)

    # Wait for the debounce threshold just in case
    # Wait for the debounce threshold just in case
    time.sleep(0.35)

    assert handler.current_process is None, "Process should not be started for read-only events"

    # Mock 'modified' event
    mock_event_modified = MagicMock()
    mock_event_modified.is_directory = False
    mock_event_modified.event_type = 'modified'
    mock_event_modified.src_path = "test.py"

    # Trigger valid event
    handler.on_any_event(mock_event_modified)

    # Wait for the debounce threshold + command execution time
    # Wait for the process to start
    start_time = time.monotonic()
    while handler.current_process is None and time.monotonic() - start_time < 3.0:
        time.sleep(0.05)

    assert handler.current_process is not None, "Process should be started for 'modified' event"

    # Cleanup
    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()

def test_stdout_capture_compatibility(capsys):  # noqa: ARG001
    """Verify that _run_command doesn't crash when sys.stdout lacks a fileno (like in pytest capsys)."""
    handler = CommandRunnerHandler("echo test_capture")

    # We pass a simple command and invoke _run_command manually
    # capsys captures stdout, making sys.stdout.fileno() throw io.UnsupportedOperation
    handler._run_command("test.py")
    _ = capsys.readouterr()  # Suppress vulture unused warning

    assert handler.current_process is not None
    handler.current_process.wait()
    assert handler.current_process.returncode == 0
