import argparse
import fnmatch
import functools
import os
import platform
import re
import signal
import subprocess
import sys
import threading
import time
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.markup import escape
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from echo.config import (
    DEFAULT_DEBOUNCE_SEC,
    DEFAULT_IGNORES,
    load_config,
    parse_debounce,
)
from echo.interactive import InteractiveController
from echo.interpolator import interpolate_command

__version__ = "1.0.0"


def format_duration(seconds: float) -> str:
    """Format duration in seconds into a human-friendly string."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f}µs"
    if seconds < 1.0:
        return f"{seconds * 1000:.1f}ms"
    return f"{seconds:.2f}s"


class EchoConsole(Console):
    """Console wrapper providing automatic ASCII transliteration and stream fallback on non-UTF-8 terminals."""

    UNICODE_FALLBACKS = {
        "✔": "[OK]",
        "✖": "[X]",
        "⚠": "[!]",
        "📡": "[*]",
        "✨": "*",
        "⏱": "[T]",
        "⏱️": "[T]",
        "🔔": "[BELL]",
        "⏸": "[PAUSE]",
        "▶": "[PLAY]",
    }

    def _write_buffer(self) -> None:
        try:
            super()._write_buffer()
        except UnicodeEncodeError:
            with self._lock:
                encoding = getattr(self.file, "encoding", None) or "utf-8"
                text = self._render_buffer(self._buffer[:])
                for char, replacement in self.UNICODE_FALLBACKS.items():
                    text = text.replace(char, replacement)
                safe_text = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
                try:
                    self.file.write(safe_text)
                    self.file.flush()
                except Exception:
                    pass
                del self._buffer[:]
        except BrokenPipeError:
            self.on_broken_pipe()
        except Exception:
            with self._lock:
                del self._buffer[:]


console = EchoConsole(legacy_windows=False)


class CommandRunnerHandler(FileSystemEventHandler):
    """Watches filesystem events, filters paths, debounces changes, and executes commands."""

    def __init__(
        self,
        command: str | None = None,
        base_path: str = ".",
        ignore_patterns: list[str] | None = None,
        debounce_sec: float | None = None,
        debounce_ms: float | None = None,
        clear_screen: bool = False,
        bell: bool = False,
        rules: list[dict[str, Any]] | None = None,
    ):
        self.command = command or ""
        self.base_path = base_path
        self._abs_base_path = os.path.join(os.path.abspath(base_path), "")
        self._abs_base_path_stripped = self._abs_base_path.rstrip(os.sep)
        self._base_prefix = os.path.join(self.base_path, "")
        self._abs_base_path_len = len(self._abs_base_path)
        self._base_prefix_len = len(self._base_prefix)

        # Debounce interval
        if debounce_sec is not None:
            self.debounce_sec = float(debounce_sec)
        elif debounce_ms is not None:
            self.debounce_sec = float(debounce_ms) / 1000.0
        else:
            self.debounce_sec = DEFAULT_DEBOUNCE_SEC

        self.clear_screen = bool(clear_screen)
        self.bell = bool(bell)
        self.rules: list[dict[str, Any]] = rules or []
        self.run_count = 0
        self.is_paused = False

        # Default ignore patterns
        default_ignores = list(DEFAULT_IGNORES)
        if ignore_patterns:
            default_ignores.extend(ignore_patterns)
        self.ignore_patterns = [p.replace("\\", "/").rstrip("/").removeprefix("./") for p in default_ignores]

        # Pre-compute exact vs wildcard patterns for faster matching
        exact_ignores = []
        wildcard_ignores = []
        for p in self.ignore_patterns:
            if "*" not in p and "?" not in p and "[" not in p:
                exact_ignores.append(p)
            else:
                wildcard_ignores.append(p)

        self.simple_exact_ignores = frozenset(p for p in exact_ignores if "/" not in p)
        self.compound_exact_ignores = frozenset(p for p in exact_ignores if "/" in p)
        self._max_compound_exact_len = max((p.count("/") + 1 for p in self.compound_exact_ignores), default=0)

        simple_wildcards = [p for p in wildcard_ignores if "/" not in p]
        compound_wildcards = [p for p in wildcard_ignores if "/" in p]

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
        self.last_event_type = "modified"
        self.is_shutting_down = False
        self.is_posix = platform.system() != "Windows"
        self.shutdown_event = threading.Event()
        self.wakeup_event = threading.Event()

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

        process._echo_terminated = True
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
        self.wakeup_event.set()
        with self.process_lock:
            self._terminate_process(self.current_process)

    def toggle_pause(self) -> bool:
        """Toggle paused state. Returns True if now paused, False if resumed."""
        self.is_paused = not self.is_paused
        if self.is_paused:
            console.print("[yellow]⏸ Echo watcher paused. File changes will be ignored. Press 'p' to resume.[/yellow]")
        else:
            console.print("[green]▶ Echo watcher resumed. Monitoring for file changes.[/green]")
        return self.is_paused

    def clear_terminal(self) -> None:
        """Clear console screen cleanly."""
        try:
            console.clear()
        except Exception:
            try:
                os.system("cls" if os.name == "nt" else "clear")
            except Exception:
                pass

    def _resolve_command(self, event_path: str, event_type: str = "modified") -> str:
        """Resolve command template via rules and interpolate file placeholders."""
        target_template = self.command

        if self.rules:
            norm_event = event_path.replace("\\", "/")
            try:
                rel_event = os.path.relpath(event_path, self.base_path).replace("\\", "/")
            except ValueError:
                rel_event = norm_event
            base_name = os.path.basename(event_path)

            for rule in self.rules:
                patterns = rule.get("patterns", [])
                cmd = rule.get("cmd")
                if not cmd:
                    continue

                for pattern in patterns:
                    pat = pattern.replace("\\", "/")
                    if fnmatch.fnmatch(norm_event, pat) or fnmatch.fnmatch(rel_event, pat) or fnmatch.fnmatch(base_name, pat):
                        target_template = cmd
                        break
                if target_template != self.command:
                    break

        if not target_template:
            return ""

        return interpolate_command(
            command_template=target_template,
            event_path=event_path,
            base_path=self.base_path,
            event_type=event_type,
        )

    def force_run(self, path: str = "manual") -> None:
        """Force an immediate re-run of configured commands."""
        with self.timer_lock:
            self.last_event_time = 0.0
            self.last_event_path = path
            self.last_event_type = "manual"
            self.wakeup_event.set()
            if self.debounce_thread is None:
                self.debounce_thread = threading.Thread(target=self._debounce_worker, daemon=True)
                self.debounce_thread.start()

    def _debounce_worker(self):
        while True:
            with self.timer_lock:
                if self.is_shutting_down:
                    self.debounce_thread = None
                    return

                now = time.monotonic()
                time_to_wait = (self.last_event_time + self.debounce_sec) - now

                if time_to_wait <= 0:
                    self.debounce_thread = None
                    path_to_run = self.last_event_path
                    type_to_run = self.last_event_type
                else:
                    path_to_run = None
                    type_to_run = "modified"

            if time_to_wait <= 0:
                if path_to_run is not None and not self.is_shutting_down:
                    try:
                        self._run_command(path_to_run, type_to_run)
                    except Exception as e:
                        try:
                            console.print(f"[bold red]Unexpected error in command runner: {escape(str(e))}[/bold red]")
                        except Exception:
                            pass
                return

            self.wakeup_event.wait(timeout=time_to_wait)
            self.wakeup_event.clear()

    def _run_command(self, event_path, event_type: str = "modified"):
        if self.is_shutting_down:
            return

        resolved_cmd = self._resolve_command(event_path, event_type)
        if not resolved_cmd:
            return

        if self.clear_screen:
            self.clear_terminal()

        try:
            self.run_count += 1
            console.print(
                f"\n[cyan]📡 Change detected in {escape(str(event_path))}. Executing: [yellow]{escape(str(resolved_cmd))}[/][/cyan]"
            )
            with self.process_lock:
                if self.is_shutting_down:
                    return

                if self.current_process and self.current_process.poll() is None:
                    console.print("[yellow]⚠ Terminating previous command...[/yellow]")
                    self._terminate_process(self.current_process)

                kwargs = {}
                if self.is_posix:
                    kwargs["start_new_session"] = True

                start_time = time.monotonic()
                process = subprocess.Popen(
                    resolved_cmd,
                    shell=True,
                    stdout=self._get_stream(sys.stdout),
                    stderr=self._get_stream(sys.stderr),
                    **kwargs,
                )
                self.current_process = process

            process.wait()
            elapsed_sec = time.monotonic() - start_time
            elapsed_str = format_duration(elapsed_sec)

            if self.bell:
                try:
                    sys.stdout.write("\a")
                    sys.stdout.flush()
                except Exception:
                    pass

            with self.process_lock:
                if self.is_shutting_down:
                    return

                if getattr(process, "_echo_terminated", False):
                    console.print(f"[yellow]✔ Command terminated by reload.[/yellow] [dim]({elapsed_str})[/dim]")
                else:
                    if process.returncode == 0:
                        console.print(
                            f"[green]✔ Command executed successfully.[/green] [dim]({elapsed_str}, run #{self.run_count})[/dim]"
                        )
                    else:
                        console.print(
                            f"[red]✖ Command failed with exit code {process.returncode}.[/red] [dim]({elapsed_str}, run #{self.run_count})[/dim]"
                        )
        except Exception as e:
            try:
                console.print(f"[bold red]Error executing command: {escape(str(e))}[/bold red]")
            except Exception:
                pass

    def _is_ignored_impl(self, path: str) -> bool:
        if path.startswith(self._abs_base_path):
            path = path[self._abs_base_path_len:]
        elif path.startswith(self._base_prefix):
            path = path[self._base_prefix_len:]
        elif path == self.base_path or path == self._abs_base_path_stripped:
            path = "."
        elif self.base_path == ".":
            pass
        else:
            try:
                path = os.path.relpath(path, self.base_path)
            except ValueError:
                pass
        if not path:
            return False

        if "\\" in path:
            path = path.replace("\\", "/")

        if "/" not in path:
            if path in self.simple_exact_ignores:
                return True
            simple_regex = self.simple_wildcard_regex
            if simple_regex and simple_regex.match(path):
                return True
            return False

        parts = path.split("/")
        if not self.simple_exact_ignores.isdisjoint(parts):
            return True

        simple_regex = self.simple_wildcard_regex
        if simple_regex:
            match = simple_regex.match
            for part in parts:
                if match(part):
                    return True

        # Check for exact and wildcard ignore patterns matching cumulative prefix directories
        if self._has_compound_ignores:
            if len(parts) > 1:
                compound_exact_ignores = self.compound_exact_ignores
                compound_regex = self.compound_wildcard_regex

                if compound_regex:
                    match = compound_regex.match
                    for start_idx in range(len(parts) - 1):
                        prefix = parts[start_idx]
                        for part in parts[start_idx + 1:]:
                            prefix = prefix + "/" + part
                            if prefix in compound_exact_ignores or match(prefix):
                                return True
                else:
                    max_len = self._max_compound_exact_len
                    for start_idx in range(len(parts) - 1):
                        prefix = parts[start_idx]
                        end_limit = min(len(parts), start_idx + max_len)
                        for part in parts[start_idx + 1:end_limit]:
                            prefix = prefix + "/" + part
                            if prefix in compound_exact_ignores:
                                return True

        return False

    def on_any_event(self, event):
        if self.is_shutting_down or self.is_paused or event.is_directory:
            return

        event_type = event.event_type
        # Ignore read-only events to prevent redundant executions
        if event_type == "opened" or event_type == "closed_no_write":
            return

        # Fast-path ignore filter to prevent infinite loops from test/build artifacts
        event_path = event.src_path

        if self._is_ignored(event_path):
            if event_type != "moved":
                return
            dest_path = getattr(event, "dest_path", None)
            if not dest_path or self._is_ignored(dest_path):
                return
            event_path = dest_path

        if not event_path:
            return

        with self.timer_lock:
            self.last_event_time = time.monotonic()
            self.last_event_path = event_path
            self.last_event_type = event_type
            self.wakeup_event.set()

            if self.debounce_thread is None:
                self.debounce_thread = threading.Thread(target=self._debounce_worker, daemon=True)
                self.debounce_thread.start()


def parse_cli_rule(rule_str: str) -> dict[str, Any]:
    """Parse a rule string in the format 'pattern1,pattern2:command'.

    Example: '*.py,tests/*.py:pytest {file}'
    """
    if ":" not in rule_str:
        raise argparse.ArgumentTypeError(
            f"Invalid rule format '{rule_str}'. Expected 'patterns:command', e.g. '*.py:pytest {{file}}'"
        )
    pats_str, cmd = rule_str.split(":", 1)
    patterns = [p.strip() for p in pats_str.split(",") if p.strip()]
    return {"patterns": patterns, "cmd": cmd.strip()}


def print_hotkey_help() -> None:
    """Print interactive mode hotkey cheat sheet."""
    console.print(
        "\n[bold cyan]Echo Interactive Shortcuts:[/bold cyan]\n"
        "  [yellow]r[/yellow] or [yellow]Enter[/yellow] : Force re-run command immediately\n"
        "  [yellow]c[/yellow]          : Clear console screen\n"
        "  [yellow]p[/yellow]          : Toggle pause / resume file observation\n"
        "  [yellow]h[/yellow] or [yellow]?[/yellow]      : Show this help summary\n"
        "  [yellow]q[/yellow]          : Clean shutdown\n"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="echo-watch",
        description="📡 Echo - High-Performance File Watcher & Task Runner (v1.0.0)",
    )
    parser.add_argument("--path", "-p", type=str, default=None, help="Directory to watch (default: current directory)")
    parser.add_argument("--cmd", "-c", type=str, default=None, help="Command to execute on change")
    parser.add_argument(
        "--ignore",
        type=str,
        default="",
        help="Comma-separated list of extra ignore patterns (e.g. '*.tmp,build,dist/*')",
    )
    parser.add_argument(
        "--debounce",
        "-d",
        type=str,
        default=None,
        help="Debounce duration before command execution (e.g. '250ms', '0.5s', '300')",
    )
    parser.add_argument(
        "--rule",
        action="append",
        type=parse_cli_rule,
        default=[],
        help="Multi-rule mapping in 'pattern:cmd' format, e.g. --rule '*.py:pytest {file}'",
    )
    parser.add_argument("--config", type=str, default=None, help="Path to config file (.echorc.json, pyproject.toml)")
    parser.add_argument("--clear", "-C", action="store_true", help="Clear terminal screen before executing commands")
    parser.add_argument("--initial", "-i", action="store_true", help="Execute command immediately on startup")
    parser.add_argument("--bell", "-b", action="store_true", help="Emit terminal audio bell on command execution")
    parser.add_argument("--no-recursive", action="store_true", help="Watch only top-level directory without recursing")
    parser.add_argument("--no-interactive", "-N", action="store_true", help="Disable interactive keyboard shortcuts")
    parser.add_argument("--version", "-v", action="version", version=f"echo {__version__}")

    args = parser.parse_args(argv)

    # 1. Load config file (either explicitly provided or auto-discovered)
    search_dir = args.path or "."
    cfg = load_config(args.config, search_dir=search_dir)

    # 2. Merge config defaults with explicit CLI arguments
    watch_path = args.path or cfg["path"] or "."
    command = args.cmd or cfg["cmd"] or ""
    clear_screen = args.clear or cfg["clear"]
    bell = args.bell or cfg["bell"]
    recursive = not args.no_recursive if args.no_recursive else cfg["recursive"]

    # Debounce
    if args.debounce is not None:
        debounce_sec = parse_debounce(args.debounce)
    else:
        debounce_sec = cfg["debounce_sec"]

    # Rules
    rules = []
    if cfg["rules"]:
        rules.extend(cfg["rules"])
    if args.rule:
        rules.extend(args.rule)

    # Extra ignores
    ignore_list = list(cfg["ignore"])
    if args.ignore:
        ignore_list.extend([p.strip() for p in args.ignore.split(",") if p.strip()])

    # Validation: Ensure at least a command or rule is configured
    if not command and not rules:
        console.print(
            "[bold red]✖ Error: No command specified.[/bold red]\n"
            "[yellow]Provide --cmd \"<command>\", define --rule \"pattern:command\", or specify rules in .echorc.json[/yellow]"
        )
        sys.exit(1)

    event_handler = CommandRunnerHandler(
        command=command,
        base_path=watch_path,
        ignore_patterns=ignore_list,
        debounce_sec=debounce_sec,
        clear_screen=clear_screen,
        bell=bell,
        rules=rules,
    )

    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=recursive)

    # Print startup banner
    cfg_note = f" (via {cfg['_loaded_from']})" if cfg.get("_loaded_from") else ""
    cmd_summary = f"[yellow]{escape(command)}[/]" if command else f"[yellow]{len(rules)} rule(s)[/]"
    console.print(
        f"[bold green]✨ Echo v{__version__} is watching [cyan]{escape(str(watch_path))}[/]{cfg_note} and running {cmd_summary}[/bold green]"
    )
    if not args.no_interactive and sys.stdin.isatty():
        console.print("[dim]Interactive mode enabled. Press [bold]h[/bold] for shortcuts, [bold]q[/bold] to quit.[/dim]")

    # Execute initial run if requested
    if args.initial:
        event_handler.force_run("startup-initial")

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

    # Interactive hotkeys
    controller: InteractiveController | None = None
    if not args.no_interactive:
        controller = InteractiveController(
            on_rerun=lambda: event_handler.force_run("manual-rerun"),
            on_clear=event_handler.clear_terminal,
            on_toggle_pause=event_handler.toggle_pause,
            on_help=print_hotkey_help,
            on_quit=lambda: os.kill(os.getpid(), signal.SIGTERM) if platform.system() != "Windows" else _windows_quit(),
        )
        controller.start()

    def _windows_quit():
        # Clean exit on Windows
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

    def handle_sigterm(_signum, _frame):
        if controller:
            controller.stop()
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
        if controller:
            controller.stop()
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
