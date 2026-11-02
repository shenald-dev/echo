import io
from unittest.mock import MagicMock

from echo.watcher import CommandRunnerHandler, EchoConsole


def test_echo_console_ascii_stream_fallback():
    raw_buffer = io.BytesIO()
    text_stream = io.TextIOWrapper(raw_buffer, encoding="ascii")
    console = EchoConsole(file=text_stream, legacy_windows=False)

    console.print("[green]✔ Command executed successfully.[/green]")
    console.print("[yellow]⚠ Terminating previous command...[/yellow]")
    console.print("[red]✖ Command failed with exit code 1.[/red]")
    console.print("[cyan]📡 Change detected in foo.py.[/cyan]")
    console.print("[magenta]✨ Echo is watching .[/magenta]")

    text_stream.flush()
    raw_buffer.seek(0)
    output = raw_buffer.read().decode("ascii")

    assert "[OK] Command executed successfully." in output
    assert "[!] Terminating previous command..." in output
    assert "[X] Command failed with exit code 1." in output
    assert "[*] Change detected in foo.py." in output
    assert "* Echo is watching ." in output


def test_echo_console_cp1252_stream_fallback():
    raw_buffer = io.BytesIO()
    text_stream = io.TextIOWrapper(raw_buffer, encoding="cp1252")
    console = EchoConsole(file=text_stream, legacy_windows=False)

    console.print("[green]✔ Command executed successfully.[/green]")
    console.print("[red]✖ Command failed with exit code 2.[/red]")

    text_stream.flush()
    raw_buffer.seek(0)
    output = raw_buffer.read().decode("cp1252")

    assert "[OK] Command executed successfully." in output
    assert "[X] Command failed with exit code 2." in output


def test_echo_console_utf8_stream_preserves_unicode():
    raw_buffer = io.BytesIO()
    text_stream = io.TextIOWrapper(raw_buffer, encoding="utf-8")
    console = EchoConsole(file=text_stream, legacy_windows=False)

    console.print("[green]✔ Command executed successfully.[/green]")
    console.print("[cyan]📡 Change detected.[/cyan]")

    text_stream.flush()
    raw_buffer.seek(0)
    output = raw_buffer.read().decode("utf-8")

    assert "✔ Command executed successfully." in output
    assert "📡 Change detected." in output


def test_echo_console_closed_stream_resilience():
    raw_buffer = io.BytesIO()
    text_stream = io.TextIOWrapper(raw_buffer, encoding="ascii")
    text_stream.close()
    console = EchoConsole(file=text_stream, legacy_windows=False)

    # Should not raise any ValueError / OSError when stream is closed
    console.print("[green]✔ Test closed stream.[/green]")


def test_echo_console_broken_pipe_handling():
    mock_file = MagicMock()
    mock_file.write.configure_mock(side_effect=BrokenPipeError("Broken pipe"))
    console = EchoConsole(file=mock_file, legacy_windows=False)

    # Must invoke on_broken_pipe() and not re-raise BrokenPipeError
    console.print("Test broken pipe")


def test_run_command_safe_on_restricted_encoding(monkeypatch):
    raw_buffer = io.BytesIO()
    text_stream = io.TextIOWrapper(raw_buffer, encoding="ascii")
    fallback_console = EchoConsole(file=text_stream, legacy_windows=False)

    import echo.watcher
    monkeypatch.setattr(echo.watcher, "console", fallback_console)

    handler = CommandRunnerHandler("echo test_safe_encoding")
    handler._run_command("test.txt")

    if handler.current_process:
        handler.current_process.wait()
    handler.shutdown()

    text_stream.flush()
    raw_buffer.seek(0)
    output = raw_buffer.read().decode("ascii")
    assert "[*] Change detected in test.txt." in output
    assert "[OK] Command executed successfully." in output


def test_debounce_worker_catches_unexpected_run_command_error(monkeypatch):
    handler = CommandRunnerHandler("echo 1")

    def failing_run_command(_path):
        raise RuntimeError("Simulated command failure")

    monkeypatch.setattr(handler, "_run_command", failing_run_command)

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.txt"
    mock_event.event_type = "modified"

    handler.on_any_event(mock_event)
    thread = handler.debounce_thread
    assert thread is not None

    # Debounce worker thread should catch the error and terminate cleanly
    # without crashing
    thread.join(timeout=2.0)
    assert not thread.is_alive()
    handler.shutdown()
