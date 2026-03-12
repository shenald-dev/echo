import sys
import time
import subprocess
import argparse
import shlex
import threading
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console

console = Console()

class CommandRunnerHandler(FileSystemEventHandler):
    def __init__(self, command: str):
        self.command = command
        self.last_run = 0.0
        self.process = None
        self.lock = threading.Lock()

    def _run_command(self, src_path):
        with self.lock:
            if self.process and self.process.poll() is None:
                console.print("[yellow]⚠ Terminating previous running command...[/yellow]")
                self.process.terminate()
                self.process.wait()

            console.print(f"\n[cyan]📡 Change detected in {src_path}. Executing: [yellow]{self.command}[/][/cyan]")
            
            try:
                # Run the command with shell=True to support pipes, redirects, &&, etc.
                self.process = subprocess.Popen(
                    self.command, 
                    shell=True, 
                    stdout=sys.stdout,
                    stderr=sys.stderr
                )

                # Capture local reference to the process for this specific thread
                current_process = self.process
            except Exception as e:
                console.print(f"[bold red]Error starting command: {e}[/bold red]")
                return

        # Wait outside the lock so we don't block new events from killing it
        current_process.wait()

        with self.lock:
            # Use the local reference to check return code, as self.process might have been overwritten
            # by a newer event that started a new thread
            if current_process.returncode is not None:
                # In Unix, negative returncode means terminated by signal (like -15 for SIGTERM)
                if current_process.returncode == 0:
                    console.print("[green]✔ Command executed successfully.[/green]")
                elif current_process.returncode < 0:
                    console.print("[yellow]⚠ Command was terminated.[/yellow]")
                else:
                    console.print(f"[red]✖ Command failed with exit code {current_process.returncode}.[/red]")

    def on_any_event(self, event):
        if event.is_directory:
            return

        current_time = time.time()
        # Simple debounce logic (1 second)
        if current_time - self.last_run > 1.0:
            self.last_run = current_time
            # Run in a background thread so we don't block the watchdog observer
            thread = threading.Thread(target=self._run_command, args=(event.src_path,))
            thread.daemon = True
            thread.start()

def main():
    parser = argparse.ArgumentParser(description="📡 Echo File Watcher")
    parser.add_argument("--path", type=str, default=".", help="Directory to watch")
    parser.add_argument("--cmd", type=str, required=True, help="Command to execute on change")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        console.print(f"[bold red]✖ Path does not exist: {args.path}[/bold red]")
        sys.exit(1)

    if not os.path.isdir(args.path):
        console.print(f"[bold red]✖ Path is not a directory: {args.path}[/bold red]")
        sys.exit(1)

    while True:
        try:
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
                observer.join()
                break # Exit the outer crash recovery loop on intentional Ctrl+C

        except Exception as e:
            console.print(f"[bold red]⚠ Watcher crashed: {e}. Restarting in 3 seconds...[/bold red]")
            try:
                observer.stop()
                observer.join()
            except:
                pass
            time.sleep(3)

if __name__ == "__main__":
    main()
