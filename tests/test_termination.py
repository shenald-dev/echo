import time
from unittest.mock import MagicMock
from unittest.mock import patch
from echo.watcher import CommandRunnerHandler

def test_unkillable_process():
    handler = CommandRunnerHandler("trap '' TERM; sleep 5")

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"

    handler.on_any_event(mock_event)
    time.sleep(0.5)

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

def test_echo_terminated_flag_is_set():
    handler = CommandRunnerHandler("sleep 5")

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"

    handler.on_any_event(mock_event)
    time.sleep(0.5)

    p1 = handler.current_process
    assert p1 is not None
    assert p1.poll() is None

    # We mock _run_command to prevent it from doing its normal wait
    # We just want to test if _terminate_process sets the flag
    with patch('echo.watcher.CommandRunnerHandler._run_command'):
        handler._terminate_process(p1)

        # the flag should be set to True
        assert getattr(p1, '_echo_terminated', False) is True

        # clean up the process manually
        if p1.poll() is None:
            p1.kill()
            p1.wait()
