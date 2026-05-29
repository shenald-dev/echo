import re
with open("tests/test_shutdown.py", "r") as f:
    content = f.read()

content = re.sub(r'<<<<<<< HEAD.*?=======\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n>>>>>>> origin/main\n', '', content, flags=re.DOTALL)

with open("tests/test_shutdown.py", "w") as f:
    f.write(content)
