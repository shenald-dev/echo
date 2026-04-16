import time
from unittest.mock import MagicMock
from echo.watcher import CommandRunnerHandler

def test_unkillable_process():
    handler = CommandRunnerHandler("trap '' TERM; sleep 5")

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"

    handler.on_any_event(mock_event)
    time.sleep(1.0)

    p1 = handler.current_process
    assert p1 is not None
    assert p1.poll() is None

    start_time = time.monotonic()
    handler.on_any_event(mock_event)

    # Wait enough for debounce + timeout + spawn new
    time.sleep(1.0)

    p2 = handler.current_process
    assert p2 is not p1
    assert p1.poll() is not None # P1 should be dead

    elapsed = time.monotonic() - start_time
    assert elapsed < 3.0, "Should not have waited 5 seconds"

    if p2:
        p2.kill()
        p2.wait()
