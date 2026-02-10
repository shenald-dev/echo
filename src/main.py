"""
Echo: Quiet, efficient dev monitoring.
"""
import time
import os
import sys
from rich.console import Console

console = Console()

class Echo:
    def __init__(self, path="."):
        self.path = os.path.abspath(path)
        self.snapshot = self._take_snapshot()

    def _take_snapshot(self):
        snapshot = {}
        for root, _, files in os.walk(self.path):
            if ".git" in root or "__pycache__" in root:
                continue
            for f in files:
                full_path = os.path.join(root, f)
                try:
                    snapshot[full_path] = os.path.getmtime(full_path)
                except OSError:
                    continue
        return snapshot

    def monitor(self):
        console.print(f"[bold cyan]📡 Echo active.[/bold cyan] Watching: [white]{self.path}[/white]")
        try:
            while True:
                time.sleep(2)
                current = self._take_snapshot()
                
                # Check for changes
                for path, mtime in current.items():
                    if path not in self.snapshot:
                        console.print(f"[green]🆕 Added:[/green] {os.path.relpath(path, self.path)}")
                    elif mtime > self.snapshot[path]:
                        console.print(f"[yellow]📝 Modified:[/yellow] {os.path.relpath(path, self.path)}")
                
                # Check for deletions
                for path in self.snapshot:
                    if path not in current:
                        console.print(f"[red]🗑️ Deleted:[/red] {os.path.relpath(path, self.path)}")
                
                self.snapshot = current
        except KeyboardInterrupt:
            console.print("\n[bold red]Stopping Echo...[/bold red]")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    echo = Echo(path)
    echo.monitor()
