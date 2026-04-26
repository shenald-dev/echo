import time
from echo.watcher import CommandRunnerHandler
import subprocess

from unittest.mock import MagicMock

def test_rich_markup_crash_escaping():
    # If the command has markup tags, it should not crash
    handler = CommandRunnerHandler("echo [/cyan]")

    # Create a mock event with a bracket in the name
    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "file_with_[bracket].txt"
    mock_event.event_type = 'modified'

    handler.on_any_event(mock_event)

    # Wait for execution
    start_time = time.monotonic()
    while handler.current_process is None and time.monotonic() - start_time < 3.0:
        time.sleep(0.05)

    assert handler.current_process is not None, "Process should have started, indicating it didn't crash"

    if handler.current_process:
        handler.current_process.terminate()
        handler.current_process.wait()


def test_rich_error_crash():
    handler = CommandRunnerHandler("echo test")

    class MockException(Exception):
        def __str__(self):
            return "File not found: [missing.py]"

    original_popen = subprocess.Popen

    def fake_popen(*args, **kwargs):
        raise MockException()

    subprocess.Popen = fake_popen
    try:
        # this should crash rich with MarkupError if not escaped
        handler._run_command("test.txt")
    finally:
        subprocess.Popen = original_popen
