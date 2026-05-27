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
from rich.markup import escape

console = Console()

class CommandRunnerHandler(FileSystemEventHandler):
    def __init__(self, command: str, base_path: str = ".", ignore_patterns: list[str] | None = None):
        self.command = command
        self.base_path = base_path
        self._abs_base_path = os.path.join(os.path.abspath(base_path), '')
        self._base_prefix = os.path.join(self.base_path, '')
        self._abs_base_path_len = len(self._abs_base_path)
        self._base_prefix_len = len(self._base_prefix)

        # Default ignore patterns
        default_ignores = [".git", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", ".venv", "venv"]
        if ignore_patterns:
            default_ignores.extend(ignore_patterns)
        self.ignore_patterns = [p.replace('\\', '/').rstrip('/').removeprefix('./') for p in default_ignores]

        # Pre-compute exact vs wildcard patterns for faster matching
        exact_ignores = [p for p in self.ignore_patterns if '*' not in p and '?' not in p and '[' not in p]
        wildcard_ignores = [p for p in self.ignore_patterns if '*' in p or '?' in p or '[' in p]

        self.simple_exact_ignores = frozenset(p for p in exact_ignores if '/' not in p)
        self.compound_exact_ignores = frozenset(p for p in exact_ignores if '/' in p)

        simple_wildcards = [p for p in wildcard_ignores if '/' not in p]
        compound_wildcards = [p for p in wildcard_ignores if '/' in p]

        self.simple_wildcard_regex = None
        self.compound_wildcard_regex = None
        self._has_compound_ignores = bool(self.compound_exact_ignores or compound_wildcards)

        if simple_wildcards:
            self.simple_wildcard_regex = re.compile("|".join(f"(?:{fnmatch.translate(p)})" for p in simple_wildcards))
        if compound_wildcards:
            self.compound_wildcard_regex = re.compile("|".join(f"(?:{fnmatch.translate(p)})" for p in compound_wildcards))

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


    def _get_stream(self, stream):
        try:
            stream.fileno()
            return stream
        except Exception:
            return None

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
        with self.process_lock:
            self._terminate_process(self.current_process)

    def _debounce_worker(self):
        while True:
            with self.timer_lock:
                if self.is_shutting_down:
                    self.debounce_thread = None
                    return

                now = time.monotonic()
                time_to_wait = (self.last_event_time + 0.25) - now

                if time_to_wait <= 0:
                    self.debounce_thread = None
                    path_to_run = self.last_event_path
                else:
                    path_to_run = None

            if time_to_wait <= 0:
                if path_to_run is not None and not self.is_shutting_down:
                    # We reached the debounce threshold, execute command
                    self._run_command(path_to_run)
                return

            # Sleep until the next check, but wake up instantly on shutdown
            self.shutdown_event.wait(timeout=time_to_wait)

    def _run_command(self, event_path):
        if self.is_shutting_down:
            return

        console.print(f"\n[cyan]📡 Change detected in {escape(str(event_path))}. Executing: [yellow]{escape(str(self.command))}[/][/cyan]")
        try:
            with self.process_lock:
                if self.is_shutting_down:
                    return

                if self.current_process and self.current_process.poll() is None:
                    console.print("[yellow]⚠ Terminating previous command...[/yellow]")
                    self._terminate_process(self.current_process)

                # Run the command with pipes to preserve output
                kwargs = {}
                if self.is_posix:
                    kwargs['start_new_session'] = True

                process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdout=self._get_stream(sys.stdout),
                    stderr=self._get_stream(sys.stderr),
                    **kwargs
                )
                self.current_process = process

            process.wait()

            with self.process_lock:
                if self.is_shutting_down:
                    return

                if getattr(process, '_echo_terminated', False): # SIGTERM or Windows termination
                    console.print("[yellow]✔ Command terminated by reload.[/yellow]")
                else:
                    if process.returncode == 0:
                        console.print("[green]✔ Command executed successfully.[/green]")
                    else:
                        console.print(f"[red]✖ Command failed with exit code {process.returncode}.[/red]")
        except Exception as e:
            console.print(f"[bold red]Error executing command: {escape(str(e))}[/bold red]")

    def _is_ignored_impl(self, path: str) -> bool:
        if path.startswith(self._abs_base_path):
            path = path[self._abs_base_path_len:]
        elif path.startswith(self._base_prefix):
            path = path[self._base_prefix_len:]
        elif path == self.base_path or path == self._abs_base_path.rstrip(os.sep):
            path = "."
        elif self.base_path == "." and not os.path.isabs(path) and not path.startswith(".."):
            pass
        else:
            try:
                path = os.path.relpath(path, self.base_path)
            except ValueError:
                pass
        if not path:
            return False

        normalized_path = path.replace('\\', '/')

        parts = normalized_path.split('/')
        if not self.simple_exact_ignores.isdisjoint(parts):
            return True

        if self.simple_wildcard_regex:
            match = self.simple_wildcard_regex.match
            for part in parts:
                if match(part):
                    return True

        # Check for exact and wildcard ignore patterns matching cumulative prefix directories
        if self._has_compound_ignores and len(parts) > 1:
            prefix = parts[0]
            compound_exact_ignores = self.compound_exact_ignores

            if self.compound_wildcard_regex:
                match = self.compound_wildcard_regex.match
                for part in parts[1:]:
                    prefix = f"{prefix}/{part}"
                    if prefix in compound_exact_ignores:
                        return True
                    if match(prefix):
                        return True
            else:
                for part in parts[1:]:
                    prefix = f"{prefix}/{part}"
                    if prefix in compound_exact_ignores:
                        return True

        return False

    def on_any_event(self, event):
        if self.is_shutting_down:
            return

        if event.is_directory:
            return
            
        # Ignore read-only events to prevent redundant executions
        if event.event_type in ('opened', 'closed_no_write'):
            return

        # Fast-path ignore filter to prevent infinite loops from test/build artifacts
        event_path = event.src_path

        is_src_ignored = event_path and self._is_ignored(event_path)
        dest_path = getattr(event, 'dest_path', None)

        if is_src_ignored:
            is_dest_ignored = dest_path and self._is_ignored(dest_path)
            if not dest_path or is_dest_ignored:
                return
            event_path = dest_path

        if not event_path:
            return

        self.last_event_time = time.monotonic()
        self.last_event_path = event_path

        if self.debounce_thread is None:
            with self.timer_lock:
                if self.debounce_thread is None:
                    self.debounce_thread = threading.Thread(target=self._debounce_worker, daemon=True)
                    self.debounce_thread.start()

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
    
    console.print(f"[bold green]✨ Echo is watching [cyan]{escape(str(args.path))}[/] and will run [yellow]{escape(str(args.cmd))}[/][/bold green]")

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

    def handle_sigterm(_signum, _frame):
        try:
            observer.stop()
        except Exception:
            pass
        try:
            console.print("\n[magenta]Echo shutting down. Peace ✨[/magenta]")
        except Exception:
            pass
        try:
            event_handler.shutdown()
        except Exception:
            pass
        sys.exit(0)

    if platform.system() != "Windows":
        signal.signal(signal.SIGTERM, handle_sigterm)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        try:
            observer.stop()
        except Exception:
            pass
        try:
            console.print("\n[magenta]Echo shutting down. Peace ✨[/magenta]")
        except Exception:
            pass
        try:
            event_handler.shutdown()
        except Exception:
            pass
    try:
        observer.join()
    except Exception:
        pass

if __name__ == "__main__":
    main()
