import os
import sys
import time
import signal
import platform
import subprocess
import argparse
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console

console = Console()

class CommandRunnerHandler(FileSystemEventHandler):
    def __init__(self, command: str):
        self.command = command
        self.current_process = None
        self.process_lock = threading.Lock()
        self.timer_lock = threading.Lock()
        self.debounce_thread = None
        self.last_event_time = 0.0
        self.last_event_path = None
        self.is_shutting_down = False

    def _terminate_process(self, process):
        if not process or process.poll() is not None:
            return

        is_posix = platform.system() != "Windows"
        if is_posix:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
        else:
            process.terminate()

        try:
            process.wait(timeout=0.25)
        except subprocess.TimeoutExpired:
            console.print("[red]⚠ Command did not terminate gracefully, killing it...[/red]")
            if is_posix:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                process.kill()
            process.wait()

    def shutdown(self):
        """Safely shuts down the handler and terminates any running process."""
        self.is_shutting_down = True
        with self.process_lock:
            self._terminate_process(self.current_process)

    def _debounce_worker(self):
        while True:
            with self.timer_lock:
                if self.is_shutting_down:
                    self.debounce_thread = None
                    return

                now = time.time()
                time_to_wait = (self.last_event_time + 0.25) - now

                if time_to_wait <= 0:
                    self.debounce_thread = None
                    path_to_run = self.last_event_path
                else:
                    path_to_run = None

            if path_to_run is not None:
                # We reached the debounce threshold, execute command
                if not self.is_shutting_down:
                    self._run_command(path_to_run)
                return

            # Sleep until the next check
            time.sleep(time_to_wait)

    def _run_command(self, event_path):
        if self.is_shutting_down:
            return

        console.print(f"\n[cyan]📡 Change detected in {event_path}. Executing: [yellow]{self.command}[/][/cyan]")
        is_posix = platform.system() != "Windows"
        try:
            with self.process_lock:
                if self.is_shutting_down:
                    return

                if self.current_process and self.current_process.poll() is None:
                    console.print("[yellow]⚠ Terminating previous command...[/yellow]")
                    self._terminate_process(self.current_process)

                # Run the command with pipes to preserve output
                kwargs = {}
                if is_posix:
                    kwargs['start_new_session'] = True

                process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    **kwargs
                )
                self.current_process = process

            process.wait()

            with self.process_lock:
                if self.current_process is process:
                    if process.returncode == 0:
                        console.print("[green]✔ Command executed successfully.[/green]")
                    elif process.returncode == -15: # SIGTERM
                        console.print("[yellow]✔ Command terminated by reload.[/yellow]")
                    else:
                        console.print(f"[red]✖ Command failed with exit code {process.returncode}.[/red]")
        except Exception as e:
            console.print(f"[bold red]Error executing command: {e}[/bold red]")


    def on_any_event(self, event):
        if getattr(self, 'is_shutting_down', False):
            return

        if event.is_directory:
            return
            
        # Ignore read-only events to prevent redundant executions
        if getattr(event, 'event_type', '') in ('opened', 'closed_no_write'):
            return

        with self.timer_lock:
            self.last_event_time = time.time()
            self.last_event_path = event.src_path

            if self.debounce_thread is None:
                self.debounce_thread = threading.Thread(target=self._debounce_worker, daemon=True)
                self.debounce_thread.start()

def main():
    parser = argparse.ArgumentParser(description="📡 Echo File Watcher")
    parser.add_argument("--path", type=str, default=".", help="Directory to watch")
    parser.add_argument("--cmd", type=str, required=True, help="Command to execute on change")
    args = parser.parse_args()

    event_handler = CommandRunnerHandler(args.cmd)
    observer = Observer()
    observer.schedule(event_handler, args.path, recursive=True)
    
    console.print(f"[bold green]✨ Echo is watching [cyan]{args.path}[/] and will run [yellow]{args.cmd}[/][/bold green]")
    observer.start()
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
