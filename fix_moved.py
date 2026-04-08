import re

with open('src/echo/watcher.py', 'r') as f:
    content = f.read()

search_str = """        # Fast-path ignore filter to prevent infinite loops from test/build artifacts
        if getattr(event, 'src_path', None) and self._is_ignored(event.src_path):
            # For moved events, check dest_path as well
            dest_path = getattr(event, 'dest_path', None)
            if not dest_path or self._is_ignored(dest_path):
                return

        with self.timer_lock:
            self.last_event_time = time.monotonic()
            self.last_event_path = event.src_path"""

replace_str = """        # Fast-path ignore filter to prevent infinite loops from test/build artifacts
        event_path = getattr(event, 'src_path', None)
        dest_path = getattr(event, 'dest_path', None)

        if event_path and self._is_ignored(event_path):
            # For moved events, check dest_path as well
            if not dest_path or self._is_ignored(dest_path):
                return
            event_path = dest_path

        with self.timer_lock:
            self.last_event_time = time.monotonic()
            self.last_event_path = event_path"""

new_content = content.replace(search_str, replace_str)

with open('src/echo/watcher.py', 'w') as f:
    f.write(new_content)
