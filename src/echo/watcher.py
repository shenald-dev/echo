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
        self.ignore_patterns = [p.replace('\\', '/').rstrip('/').removeprefix('./') for p in default_ignores]

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

        setattr(process, '_echo_terminated', True)
        try:
            if self.is_posix:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
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
        if self.debounce_thread:
            self.debounce_thread.join(timeout=1.0)
        self._terminate_process(self.current_process)

    def _is_ignored_impl(self, path: str) -> bool:
        """Check if a path should be ignored based on ignore patterns."""
        # Make path relative to base_path for consistent matching
        try:
            rel_path = os.path.relpath(path, self.base_path)
        except ValueError:
            # If base_path is not a parent of path, treat as absolute
            rel_path = path
        
        # Normalize path separators
        rel_path = rel_path.replace('\\', '/')
        
        # Check exact matches first
        if rel_path in self.exact_ignores:
            return True
            
        # Check wildcard patterns
        if self.wildcard_regex and self.wildcard_regex.match(rel_path):
            return True
            
        return False

    def on_any_event(self, event):
        if getattr(self, 'is_shutting_down', False):
            return

        if event.is_directory:
            return
            
        # Ignore read-only events to prevent redundant executions
        if getattr(event, 'event_type', '') in ('opened', 'closed_no_write'):
            return

        # Fast-path ignore filter to prevent infinite loops from test/build artifacts
        event_path = getattr(event, 'src_path', None)

        is_src_ignored = event_path and self._is_ignored(event_path)
        dest_path = getattr(event, 'dest_path', None)

        if is_src_ignored:
            is_dest_ignored = dest_path and self._is_ignored(dest_path)
            if not dest_path or is_dest_ignored:
                return
            event_path = dest_path

        with self.timer_lock:
            self.last_event_time = time.monotonic()
            self.last_event_path = event_path

            if self.debounce_thread is None:
                self.debounce_thread = threading.Thread(target=self._debounce_worker, daemon=True)
                self.debounce_thread.start()

    def _debounce_worker(self):
        """Worker thread that waits for the debounce period and then runs the command."""
        while not self.shutdown_event.is_set():
            with self.timer_lock:
                now = time.monotonic()
                elapsed = now - self.last_event_time
                if elapsed >= 0.5:  # 500ms debounce
                    if self.last_event_path is not None:
                        self._run_command()
                    self.last_event_path = None
                    self.debounce_thread = None
                    return
                # Sleep for the remaining time or until shutdown
                timeout = min(0.5 - elapsed, 0.1)
            self.shutdown_event.wait(timeout=timeout)

    def _run_command(self):
        """Run the command in a subprocess."""
        with self.process_lock:
            # Terminate any existing process
            if self.current_process:
                self._terminate_process(self.current_process)
            
            # Start new process
            try:
                console.print(f"[blue]▶ Running: {self.command}[/blue]")
                if self.is_posix:
                    self.current_process = subprocess.Popen(
                        self.command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        preexec_fn=os.setsid,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                else:
                    self.current_process = subprocess.Popen(
                        self.command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                
                # Stream output in real-time
                for line in iter(self.current_process.stdout.readline, ''):
                    if line:
                        console.print(line, end='')
                
                self.current_process.stdout.close()
                return_code = self.current_process.wait()
                if return_code:
                    console.print(f"[red]✖ Command failed with exit code {return_code}[/red]")
                else:
                    console.print(f"[green]✓ Command completed successfully[/green]")
                    
            except Exception as e:
                console.print(f"[red]✖ Error running command: {e}[/red]")
            finally:
                self.current_process = None

def main():
    parser = argparse.ArgumentParser(description="📡 Echo File Watcher")
    parser.add_argument("--path", type=str, default=".", help="Directory to watch")
    parser.add_argument("--cmd", type=str, required=True, help="Command to execute on change")
    parser.add_argument("--ignore", type=str, default="", help="Comma-separated list of extra ignore patterns (e.g. '*.tmp,build')")
    args = parser.parse_args()

    ignore_patterns = [p.strip() for p in args.ignore.split(",") if p.strip()] if args.ignore else None
    event_handler = CommandRunnerHandler(args.cmd, base_path=args.path, ignore_patterns=ignore_patterns)
    observer = Observer()
    observer.schedule(event_handler, args.path, recursive=True)
    
    console.print(f"[bold green]✨ Echo is watching [cyan]{args.path}[/] and will run [yellow]{args.cmd}[/][/bold green]")

    try:
        observer.start()
    except OSError as e:
        if "Inotify watch limit reached" in str(e) or getattr(e, "errno", None) == 28:
            console.print(
                "\n[bold red]✖ Error: OS inotify watch limit reached.[/bold red]\n"
                "[yellow]Your system is configured to limit the number of files that can be watched.\n"
                "You can fix this by increasing the limit. Run the following command:[/yellow]\n\n"
                "  [cyan]echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p[/cyan]\n"
            )
            sys.exit(1)
        raise

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        console.print("\n[magenta]Echo shutting down. Peace ✨[/magenta]")
        event_handler.shutdown()

    observer.join()

if __name__ == "__main__":
    main()