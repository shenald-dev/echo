with open("src/echo/watcher.py", "r") as f:
    content = f.read()

import re
content = re.sub(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> origin/main\n', r'\1\n', content, flags=re.DOTALL)

with open("src/echo/watcher.py", "w") as f:
    f.write(content)
