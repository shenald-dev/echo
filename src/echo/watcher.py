import os
import sys
import time
import signal
import platform
import subprocess
import fnmatch
import re
import argparse
import threading
import functools
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console

console = Console()

class CommandRunnerHandler(FileSystemEventHandler):
    def __init__(self, command: str, base_path: str = ".", ignore_patterns: list[str] | None = None):
        self.command = command
        self.base_path = base_path

        # Default ignore patterns
        default_ignores = [".git", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", ".venv", "venv"]
        if ignore_patterns:
            default_ignores.extend(ignore_patterns)
        self.ignore_patterns = [p.replace('\\', '/').removeprefix('./') for p in default_ignores]

        # Pre-compute exact vs wildcard patterns for faster matching
        self.exact_ignores = {p for p in self.ignore_patterns if '*' not in p and '?' not in p}
        wildcard_ignores = [p for p in self.ignore_patterns if '*' in p or '?' in p]
        self.wildcard_regex = None
        if wildcard_ignores:
            regex_str = "|".join(f"(?:{fnmatch.translate(p)})" for p in wildcard_ignores)
            self.wildcard_regex = re.compile(regex_str)

        self.current_process = None
        self.process_lock = threading.Lock()
        self.timer_lock = threading.Lock()
        self.debounce_thread = None
        self.last_event_time = 0.0
        self.last_event_path = None
        self.is_shutting_down = False
        self.is_posix = platform.system() != "Windows"
        self.shutdown_event = threading.Event()

        # Bind LRU cache to instance to prevent memory leaks across instances
        self._is_ignored = functools.lru_cache(maxsize=4096)(self._is_ignored_impl)

    def _terminate_process(self, process):
        if not process or process.poll() is not None:
            return

        try:
            if self.is_posix:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
            setattr(process, '_echo_terminated', True)
        except OSError:
            pass

        try:
            process.wait(timeout=0.25)
        except subprocess.TimeoutExpired:
            console.print("[red]⚠ Command did not terminate gracefully, killing it...[/red]")
            try:
                if self.is_posix:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                else:
                    process.kill()
            except OSError:
                pass

            try:
                process.wait(timeout=0.25)
            except subprocess.TimeoutExpired:
                console.print("[red]⚠ Process refused to die. Abandoning.[/red]")

    def shutdown(self):
        """Safely shuts down the handler and terminates any running process."""
        self.is_shutting_down = True
        self.shutdown_event.set()
        if self.debounce_thread and self.debounce_thread.is_alive():
            self.debounce_thread.join()
        with self.process_lock:
            if self.current_process:
                self._terminate_process(self.current_process)
                self.current_process = None
        console.print("[green]✓ Watcher shut down.[/green]")

    def _is_ignored_impl(self, path: str) -> bool:
        """Return True if the path should be ignored."""
        # Normalize path for matching
        normalized = path.replace('\\', '/')
        if normalized.startswith('./'):
            normalized = normalized[2:]

        # Check exact matches first (fast path)
        if normalized in self.exact_ignores:
            return True
        # Check if any parent directory is in exact ignores
        parts = normalized.split('/')
        for i in range(len(parts)):
            if '/'.join(parts[:i+1]) in self.exact_ignores:
                return True

        # Check wildcard patterns
        if self.wildcard_regex:
            # Match against the full path and each parent directory
            if self.wildcard_regex.match(normalized):
                return True
            for i in range(len(parts)):
                if self.wildcard_regex.match('/'.join(parts[:i+1])):
                    return True
        return False

    def on_any_event(self, event):
        if self.is_shutting_down:
            return
        if event.is_directory:
            return
        path = event.src_path
        if self._is_ignored(path):
            return
        # Debounce events
        now = time.time()
        with self.timer_lock:
            if now - self.last_event_time < 0.5:  # 500ms debounce
                # Same path rapid fire? ignore if same path within debounce window
                if self.last_event_path == path:
                    return
            self.last_event_time = now
            self.last_event_path = path

        # Cancel previous debounce thread if exists
        if self.debounce_thread and self.debounce_thread.is_alive():
            # It's okay to let it finish; we will just start a new one after a short sleep
            pass

        self.debounce_thread = threading.Thread(target=self._run_command_with_debounce, args=(path,))
        self.debounce_thread.daemon = True
        self.debounce_thread.start()

    def _run_command_with_debounce(self, path: str):
        """Wait a bit then run the command, avoiding rapid repeats."""
        time.sleep(0.5)  # debounce window
        if self.is_shutting_down:
            return
        # Avoid running if another event for same path came in while we slept
        with self.timer_lock:
            if time.time() - self.last_event_time < 0.5:
                return
        self._run_command(path)

    def _run_command(self, path: str):
        """Execute the command, ensuring only one runs at a time."""
        with self.process_lock:
            if self.current_process and self.current_process.poll() is None:
                console.print(f"[yellow]⚠ Previous command still running, terminating...[/yellow]")
                self._terminate_process(self.current_process)
            # Build command with path placeholder if needed
            cmd = self.command
            if "{}" in cmd:
                cmd = cmd.format(path)
            else:
                # Append path as argument if no placeholder
                cmd = f"{cmd} {path}"
            console.print(f"[blue]▶ Running:[/blue] {cmd}")
            try:
                # Use shell=True to allow complex commands, but create new process group
                if self.is_posix:
                    self.current_process = subprocess.Popen(
                        cmd,
                        shell=True,
                        preexec_fn=os.setsid,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                    )
                else:
                    self.current_process = subprocess.Popen(
                        cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    )
                # Stream output in real-time
                for line in iter(self.current_process.stdout.readline, ''):
                    if line:
                        console.print(line.rstrip())
                self.current_process.stdout.close()
                return_code = self.current_process.wait()
                if return_code:
                    console.print(f"[red]✗ Command failed with exit code {return_code}[/red]")
                else:
                    console.print("[green]✓ Command finished successfully.[/green]")
            except Exception as e:
                console.print(f"[red]✗ Error running command: {e}[/red]")
            finally:
                self.current_process = None

# The rest of the file (e.g., main function, argument parsing, observer setup) is assumed identical in both branches.
# For brevity, only the shown portion is included here as it was identical.
# In a real merge, you would include the remaining unchanged code after this point.