import time
import threading
from echo.watcher import CommandRunnerHandler
from unittest.mock import MagicMock

def test_debounce_thread_safety():
    handler = CommandRunnerHandler("echo test")

    # Create multiple concurrent events to trigger race condition
    def trigger_event(path):
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = path
        mock_event.event_type = "modified"
        handler.on_any_event(mock_event)

    threads = []
    for i in range(20):
        t = threading.Thread(target=trigger_event, args=(f"test{i}.txt",))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Wait for the debounce worker to pick up the final event
    start = time.time()
    while handler.current_process is None and time.time() - start < 2:
        time.sleep(0.05)

    if handler.current_process:
        handler.current_process.wait()

    # Ensure it didn't crash and actually processed an event
    assert handler.last_event_path is not None
