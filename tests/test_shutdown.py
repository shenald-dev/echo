from echo.watcher import CommandRunnerHandler
from unittest.mock import MagicMock

def test_shutdown_prevents_execution():
    handler = CommandRunnerHandler("sleep 10")

    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.src_path = "test.py"

    # Trigger event
    handler.on_any_event(mock_event)

    # Capture thread reference before shutdown
    thread = handler.debounce_thread

    # Simulate shutdown
    handler.shutdown()

    # Wait for debounce thread to finish via event instantly instead of sleep
    if thread:
        thread.join(timeout=2.0)

    assert handler.current_process is None or handler.current_process.poll() is not None


def test_shutdown_exception_isolation():
    from echo.watcher import main
    from unittest.mock import patch, MagicMock

    mock_observer = MagicMock()
    mock_observer.stop.configure_mock(side_effect=Exception("Observer crash"))
    mock_handler = MagicMock()

    with patch("echo.watcher.Observer", return_value=mock_observer), \
         patch("echo.watcher.CommandRunnerHandler", return_value=mock_handler), \
         patch("echo.watcher.console.print"), \
         patch("sys.exit"), \
         patch("sys.argv", ["echo-watch", "--cmd", "echo 1"]):

        # Test handle_sigterm
        # We can simulate calling the sigterm handler
        with patch("signal.signal"):
            from echo.watcher import main

            # Since main blocks, we need to mock time.sleep to raise KeyboardInterrupt
            with patch("time.sleep", side_effect=KeyboardInterrupt):
                main()

            # Now verify observer.stop was called AND handler.shutdown was called
            # despite the exception in observer.stop
            assert mock_observer.stop.call_count == 1
            assert mock_handler.shutdown.call_count == 1
```