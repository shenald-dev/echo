import time
from unittest import mock
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

@mock.patch("echo.watcher.os.killpg")
@mock.patch("echo.watcher.platform.system", return_value="Linux")
def test_termination_flag_set_before_killpg(mock_system, mock_killpg):
    handler = CommandRunnerHandler("echo 1")

    # Create a mock process
    class MockProcess:
        def __init__(self):
            self.pid = 12345
            self.wait_called = False
        def poll(self):
            return None
        def wait(self, timeout=None):
            self.wait_called = True

    mock_process = MockProcess()

    # Assert _echo_terminated is NOT set before call
    assert not hasattr(mock_process, "_echo_terminated")

    def side_effect(*args, **kwargs):
        # When killpg is called, the flag should ALREADY be True
        assert getattr(mock_process, "_echo_terminated", False) is True

    mock_killpg.side_effect = side_effect

    with mock.patch("echo.watcher.os.getpgid", return_value=12345):
        handler._terminate_process(mock_process)

    mock_killpg.assert_called_once()
    assert getattr(mock_process, "_echo_terminated", False) is True
