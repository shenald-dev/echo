import os
import sys
import time
from unittest.mock import MagicMock

from echo.watcher import CommandRunnerHandler


def is_pid_alive(pid: int) -> bool:
    if sys.platform == "win32":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000 | 0x00100000, False, pid)
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return exit_code.value == 259
            return False
        finally:
            kernel32.CloseHandle(handle)
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def test_unkillable_process():
    if os.name == 'nt':
        cmd = f'"{sys.executable}" -c "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(5)"'
    else:
        cmd = "trap '' TERM; sleep 5"
    handler = CommandRunnerHandler(cmd)

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"

    handler.on_any_event(mock_event)
    # Wait for process to start
    start_time_wait = time.monotonic()
    while handler.current_process is None and time.monotonic() - start_time_wait < 3.0:
        time.sleep(0.05)
    p1 = handler.current_process
    assert p1 is not None
    assert p1.poll() is None

    start_time = time.monotonic()
    handler.on_any_event(mock_event)

    # Wait enough for debounce + timeout + spawn new
    start_time_wait = time.monotonic()
    while (handler.current_process is None or handler.current_process is p1) and time.monotonic() - start_time_wait < 3.0:
        time.sleep(0.05)

    p2 = handler.current_process
    assert p2 is not p1
    assert p1.poll() is not None  # P1 should be dead

    elapsed = time.monotonic() - start_time
    assert elapsed < 3.0, "Should not have waited 5 seconds"

    if p2:
        p2.kill()
        p2.wait()
    handler.shutdown()
    if handler.debounce_thread:
        handler.debounce_thread.join(timeout=1.0)


def test_process_tree_termination_on_reload(tmp_path):
    pid_file = tmp_path / "child_reload.pid"
    pid_file_str = str(pid_file).replace("\\", "/")
    code = f"import os, time; open('{pid_file_str}', 'w').write(str(os.getpid())); time.sleep(30)"
    cmd = f'"{sys.executable}" -c "{code}"'
    handler = CommandRunnerHandler(cmd, debounce_sec=0.05)

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"
    mock_event.event_type = "modified"

    handler.on_any_event(mock_event)

    start_time = time.monotonic()
    while not pid_file.exists() or pid_file.stat().st_size == 0:
        if time.monotonic() - start_time > 5.0:
            raise TimeoutError("Timed out waiting for child process to start")
        time.sleep(0.05)

    child_pid = int(pid_file.read_text().strip())
    assert is_pid_alive(child_pid)

    # Trigger second event to cause reload
    handler.on_any_event(mock_event)

    start_time = time.monotonic()
    while is_pid_alive(child_pid) and time.monotonic() - start_time < 5.0:
        time.sleep(0.05)

    assert not is_pid_alive(child_pid), f"Child process {child_pid} was orphaned after reload"

    handler.shutdown()
    if handler.debounce_thread:
        handler.debounce_thread.join(timeout=1.0)


def test_process_tree_termination_on_shutdown(tmp_path):
    pid_file = tmp_path / "child_shutdown.pid"
    pid_file_str = str(pid_file).replace("\\", "/")
    code = f"import os, time; open('{pid_file_str}', 'w').write(str(os.getpid())); time.sleep(30)"
    cmd = f'"{sys.executable}" -c "{code}"'
    handler = CommandRunnerHandler(cmd, debounce_sec=0.05)

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"
    mock_event.event_type = "modified"

    handler.on_any_event(mock_event)

    start_time = time.monotonic()
    while not pid_file.exists() or pid_file.stat().st_size == 0:
        if time.monotonic() - start_time > 5.0:
            raise TimeoutError("Timed out waiting for child process to start")
        time.sleep(0.05)

    child_pid = int(pid_file.read_text().strip())
    assert is_pid_alive(child_pid)

    handler.shutdown()
    if handler.debounce_thread:
        handler.debounce_thread.join(timeout=1.0)

    start_time = time.monotonic()
    while is_pid_alive(child_pid) and time.monotonic() - start_time < 5.0:
        time.sleep(0.05)

    assert not is_pid_alive(child_pid), f"Child process {child_pid} was orphaned after shutdown"


def test_process_termination_taskkill_fallback(monkeypatch):
    """Verify that when taskkill fails or raises, fallback termination is still executed."""
    import subprocess

    def failing_run(*args, **kwargs):
        raise OSError("taskkill failed")

    monkeypatch.setattr(subprocess, "run", failing_run)

    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    mock_proc.pid = 12345
    mock_proc.wait.return_value = 0

    handler = CommandRunnerHandler("echo test")
    handler.is_posix = False
    handler._terminate_process(mock_proc)

    mock_proc.terminate.assert_called_once()
    mock_proc.wait.assert_called()
