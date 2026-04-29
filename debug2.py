from echo.watcher import CommandRunnerHandler
handler = CommandRunnerHandler("echo 1", ignore_patterns=["b/c"])
print(handler.exact_ignores)
print(handler._is_ignored_impl("a/b/c/d.py"))
