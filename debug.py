from echo.watcher import CommandRunnerHandler
handler = CommandRunnerHandler("echo 1", ignore_patterns=["node_modules/express"])
print(handler.exact_ignores)
print(handler._is_ignored_impl("src/node_modules/express/index.js"))
