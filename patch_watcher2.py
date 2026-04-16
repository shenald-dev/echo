with open("src/echo/watcher.py", "r") as f:
    content = f.read()

import re
content = re.sub(r'elif getattr\(process, \\\'_echo_terminated\\\', False\):', r'elif getattr(process, \'_echo_terminated\', False):', content)

with open("src/echo/watcher.py", "w") as f:
    f.write(content)
