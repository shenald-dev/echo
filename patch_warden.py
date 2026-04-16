with open(".jules/warden.md", "r") as f:
    content = f.read()

import re
content = re.sub(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> origin/main\n', r'\1\n\2\n', content, flags=re.DOTALL)

with open(".jules/warden.md", "w") as f:
    f.write(content)
