import re

with open("src/echo/watcher.py", "r") as f:
    content = f.read()

content = re.sub(
    r"<<<<<<< HEAD\n=======\n        self._abs_base_path_len = len\(self._abs_base_path\)\n>>>>>>> origin/main\n",
    "",
    content
)

with open("src/echo/watcher.py", "w") as f:
    f.write(content)
