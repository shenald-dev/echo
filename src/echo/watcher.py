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

    def _debounce_worker(self):
        while True:
            with self.timer_lock:
                now = time.time()
                time_to_wait = (self.last_event_time + 0.25) - now

                if time_to_wait <= 0:
                    self.debounce_thread = None
                    path_to_run = self.last_event_path
                else:
                    path_to_run = None

            if path_to_run is not None:
                # We reached the debounce threshold, execute command
                self._run_command(path_to_run)
                return

            # Sleep until the next check
            time.sleep(time_to_wait)

    def _run_command(self, event_path):
        console.print(f"\n[cyan]📡 Change detected in {event_path}. Executing: [yellow]{self.command}[/][/cyan]")
        is_posix = platform.system() != "Windows"
        try:
            with self.process_lock:
                if self.current_process and self.current_process.poll() is None:
                    console.print("[yellow]⚠ Terminating previous command...[/yellow]")
                    if is_posix:
                        try:
                            os.killpg(os.getpgid(self.current_process.pid), signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                    else:
                        self.current_process.terminate()
                    self.current_process.wait()

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
        if event_handler.current_process and event_handler.current_process.poll() is None:
            if platform.system() != "Windows":
                try:
                    os.killpg(os.getpgid(event_handler.current_process.pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
            else:
                event_handler.current_process.terminate()
            event_handler.current_process.wait()

    observer.join()

if __name__ == "__main__":
    main()
