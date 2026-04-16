import time
from unittest.mock import MagicMock, patch
from echo.watcher import CommandRunnerHandler
import subprocess
import os

@patch("os.killpg")
def test_termination_intent_with_oserror(mock_killpg):
    # Simulate an OSError during os.killpg
    mock_killpg.side_effect = OSError("Simulated OSError")

    handler = CommandRunnerHandler("echo 'test'")

    # Create a dummy process mock
    mock_process = MagicMock()
    mock_process.poll.return_value = None
    mock_process.pid = 12345

    # Simulate current process
    handler.current_process = mock_process

    # Trigger termination
    handler._terminate_process(mock_process)

    # Ensure the _echo_terminated flag was set despite the OSError
    assert getattr(mock_process, '_echo_terminated', False) is True
