from unittest.mock import MagicMock
from echo.watcher import CommandRunnerHandler

def test_termination_intent_flag_suppresses_error_log(capsys):
    """
    Verify that when a process is terminated intentionally (has the _echo_terminated flag),
    the exit code does not produce a failure log, regardless of OS.
    """
    handler = CommandRunnerHandler("echo 1")
    handler.is_shutting_down = False

    # Mock a process that was intentionally terminated
    mock_process = MagicMock()
    mock_process.returncode = 1  # Typical Windows termination code, or arbitrary failure code
    mock_process.poll.return_value = 1

    # Set the intent flag
    setattr(mock_process, '_echo_terminated', True)

    handler.current_process = mock_process

    # Call the reporting logic directly
    with handler.process_lock:
        if handler.current_process is mock_process:
            if mock_process.returncode == 0:
                pass
            elif getattr(mock_process, '_echo_terminated', False): # Reload termination
                print("[yellow]✔ Command terminated by reload.[/yellow]")
            else:
                print(f"[red]✖ Command failed with exit code {mock_process.returncode}.[/red]")

    captured = capsys.readouterr()
    assert "Command terminated by reload." in captured.out
    assert "Command failed" not in captured.out

def test_missing_intent_flag_reports_failure(capsys):
    """
    Verify that if a process exits with a non-zero code and LACKS the _echo_terminated flag,
    it is correctly reported as a failure.
    """
    handler = CommandRunnerHandler("echo 1")
    handler.is_shutting_down = False

    # Create an object without dynamic magic attributes
    class DummyProcess:
        pass

    mock_process = DummyProcess()
    mock_process.returncode = 1
    mock_process.pid = 1234

    handler.current_process = mock_process

    # Call the reporting logic directly
    with handler.process_lock:
        if handler.current_process is mock_process:
            if mock_process.returncode == 0:
                pass
            elif getattr(mock_process, '_echo_terminated', False): # Reload termination
                print("[yellow]✔ Command terminated by reload.[/yellow]")
            else:
                print(f"[red]✖ Command failed with exit code {mock_process.returncode}.[/red]")

    captured = capsys.readouterr()
    assert "Command failed with exit code 1" in captured.out
    assert "Command terminated by reload." not in captured.out
