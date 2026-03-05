import sys
import time
import subprocess
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console

console = Console()

class CommandRunnerHandler(FileSystemEventHandler):
    def __init__(self, command: str):
        self.command = command
        self.last_run = 0.0

    def on_any_event(self, event):
        if event.is_directory:
            return
            
        current_time = time.time()
        # Simple debounce logic (1 second)
        if current_time - self.last_run > 1.0:
            self.last_run = current_time
            console.print(f"\n[cyan]📡 Change detected in {event.src_path}. Executing: [yellow]{self.command}[/][/cyan]")
            
            try:
                # Run the command with pipes to preserve output
                process = subprocess.Popen(
                    self.command, 
                    shell=True, 
                    stdout=sys.stdout,
                    stderr=sys.stderr
                )
                process.wait()
                if process.returncode == 0:
                    console.print("[green]✔ Command executed successfully.[/green]")
                else:
                    console.print(f"[red]✖ Command failed with exit code {process.returncode}.[/red]")
            except Exception as e:
                console.print(f"[bold red]Error executing command: {e}[/bold red]")

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
    observer.join()

if __name__ == "__main__":
    main()
