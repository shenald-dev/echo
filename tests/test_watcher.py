import os
import time
import pytest
import threading
from watchdog.events import FileModifiedEvent
from echo.watcher import CommandRunnerHandler

def test_debounce_logic():
    handler = CommandRunnerHandler("echo test")

    # Simulate a file modification event
    event = FileModifiedEvent("test.txt")

    # First call should trigger execution
    handler.on_any_event(event)
    assert handler.last_run > 0

    last_run = handler.last_run

    # Immediate second call should be debounced
    handler.on_any_event(event)
    assert handler.last_run == last_run

    # Wait for more than 1 second to pass the debounce threshold
    time.sleep(1.1)

    # Third call should trigger execution again
    handler.on_any_event(event)
    assert handler.last_run > last_run

def test_command_execution():
    # Test a command that works
    handler = CommandRunnerHandler("echo hello")
    event = FileModifiedEvent("test.txt")

    handler.on_any_event(event)
    # Wait for the background thread to finish executing
    time.sleep(0.5)

    assert handler.process is not None
    assert handler.process.returncode == 0

def test_command_termination():
    # Test a command that sleeps, so it can be terminated
    handler = CommandRunnerHandler("sleep 2")
    event = FileModifiedEvent("test.txt")

    handler.on_any_event(event)
    time.sleep(0.1) # Let the process start

    assert handler.process is not None
    assert handler.process.poll() is None # Still running

    first_process = handler.process

    # Force another event by hacking last_run
    handler.last_run = 0
    handler.on_any_event(event)

    time.sleep(0.5) # Let the old process terminate and new one start

    # Ensure the first process was terminated
    assert first_process.poll() is not None
    assert first_process.returncode < 0 # Terminated by signal

    # Ensure the new process is running
    assert handler.process is not first_process
    assert handler.process.poll() is None # Still running

    # Wait for the second one to finish
    handler.process.wait()

def test_invalid_command():
    handler = CommandRunnerHandler("invalid_command_that_does_not_exist")
    event = FileModifiedEvent("test.txt")

    handler.on_any_event(event)
    time.sleep(0.5)

    # The command should fail to start, so process might be None or returncode != 0
    # The actual Exception is caught and printed by _run_command
    pass # As long as it doesn't crash the main thread
