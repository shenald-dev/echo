"""Interactive keyboard hotkey controller for Echo terminal sessions."""

import os
import sys
import threading
import time
from typing import Callable


class InteractiveController:
    """Listens for single-character hotkeys in a terminal session.

    Supported Keys:
      - 'r' / Enter: Force re-run command
      - 'c': Clear console screen
      - 'p': Toggle pause / resume watcher
      - 'h' / '?': Display hotkey help
      - 'q': Clean shutdown
    """

    def __init__(
        self,
        on_rerun: Callable[[], None],
        on_clear: Callable[[], None],
        on_toggle_pause: Callable[[], None],
        on_help: Callable[[], None],
        on_quit: Callable[[], None],
    ):
        self.on_rerun = on_rerun
        self.on_clear = on_clear
        self.on_toggle_pause = on_toggle_pause
        self.on_help = on_help
        self.on_quit = on_quit

        self.shutdown_event = threading.Event()
        self.listener_thread: threading.Thread | None = None
        self._is_posix = os.name != "nt"

    def is_supported(self) -> bool:
        """Check if current environment has an interactive TTY."""
        try:
            return sys.stdin.isatty()
        except Exception:
            return False

    def start(self) -> bool:
        """Start the keyboard listener thread if TTY is supported."""
        if not self.is_supported():
            return False

        self.listener_thread = threading.Thread(
            target=self._listen_loop,
            name="EchoInteractiveListener",
            daemon=True,
        )
        self.listener_thread.start()
        return True

    def stop(self) -> None:
        """Signal listener loop to terminate."""
        self.shutdown_event.set()

    def _listen_loop(self) -> None:
        if self._is_posix:
            self._listen_posix()
        else:
            self._listen_windows()

    def _listen_windows(self) -> None:
        try:
            import msvcrt
        except ImportError:
            return

        while not self.shutdown_event.is_set():
            try:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    self._dispatch_key(ch)
                else:
                    time.sleep(0.05)
            except Exception:
                time.sleep(0.1)

    def _listen_posix(self) -> None:
        try:
            import select
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
        except Exception:
            return

        try:
            tty.setcbreak(fd)
            while not self.shutdown_event.is_set():
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                if rlist:
                    ch = sys.stdin.read(1)
                    self._dispatch_key(ch)
        except Exception:
            pass
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except Exception:
                pass

    def _dispatch_key(self, ch: str) -> None:
        key = ch.lower()
        if key in ("r", "\r", "\n"):
            self.on_rerun()
        elif key == "c":
            self.on_clear()
        elif key == "p":
            self.on_toggle_pause()
        elif key in ("h", "?"):
            self.on_help()
        elif key == "q":
            self.on_quit()
