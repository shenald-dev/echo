with open("src/echo/watcher.py", "r") as f:
    content = f.read()

# Replace the specific line in watcher.py
old_comment = "        # Ignore read-only events to prevent redundant executions"
new_comment = "        # Ignore read-only events to prevent redundant executions\n        # Note: watchdog's FileSystemEvent guarantees 'event_type' and 'src_path' exist."
content = content.replace(old_comment, new_comment)

with open("src/echo/watcher.py", "w") as f:
    f.write(content)
