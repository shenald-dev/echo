import sys

content = open("src/echo/watcher.py").read()

conflict = """<<<<<<< HEAD
    def handle_sigterm(signum, frame):
        observer.stop()
        console.print("\\n[magenta]Echo shutting down. Peace ✨[/magenta]")
        event_handler.shutdown()
        sys.exit(0)

    if platform.system() != "Windows":
        if signal.getsignal(signal.SIGTERM) != handle_sigterm:
            signal.signal(signal.SIGTERM, handle_sigterm)
=======
    def handle_sigterm(_signum, _frame):
        try:
            observer.stop()
            console.print("\\n[magenta]Echo shutting down. Peace ✨[/magenta]")
            event_handler.shutdown()
        except Exception:
            pass
        sys.exit(0)

    if platform.system() != "Windows":
        signal.signal(signal.SIGTERM, handle_sigterm)
>>>>>>> origin/main"""

resolution = """    def handle_sigterm(_signum, _frame):
        try:
            observer.stop()
            console.print("\\n[magenta]Echo shutting down. Peace ✨[/magenta]")
            event_handler.shutdown()
        except Exception:
            pass
        sys.exit(0)

    if platform.system() != "Windows":
        if signal.getsignal(signal.SIGTERM) != handle_sigterm:
            signal.signal(signal.SIGTERM, handle_sigterm)"""

content = content.replace(conflict, resolution)

with open("src/echo/watcher.py", "w") as f:
    f.write(content)
