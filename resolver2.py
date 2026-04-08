with open("src/echo/watcher.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.startswith("                return") and "Fast-path ignore filter" in lines[i-1]:
        # This is where the syntax error is, the resolver script previously appended `return` out of order
        pass
    elif line.startswith("        with self.timer_lock:") and "return" in lines[i-2]:
        pass
    elif line.startswith("            self.last_event_time = time.monotonic()") and "timer_lock" in lines[i-1]:
        pass
    elif line.startswith("        trigger_path = event.src_path"):
        new_lines.append(line)
    elif line.startswith("        if getattr(event, 'src_path', None) and self._is_ignored(event.src_path):"):
        new_lines.append(line)
    elif line.startswith("            # For moved events, check dest_path as well"):
        new_lines.append(line)
    elif line.startswith("            dest_path = getattr(event, 'dest_path', None)"):
        new_lines.append(line)
    elif line.startswith("            if not dest_path or self._is_ignored(dest_path):"):
        new_lines.append(line)
        new_lines.append("                return\n")
    elif line.startswith("                return") and "if not dest_path" in lines[i-1]:
        pass # Already added
    elif line.startswith("            trigger_path = dest_path"):
        new_lines.append(line)
        new_lines.append("\n")
        new_lines.append("        with self.timer_lock:\n")
        new_lines.append("            self.last_event_time = time.monotonic()\n")
    elif line.startswith("        with self.timer_lock:") and "trigger_path = dest_path" in lines[i-2]:
        pass
    elif line.startswith("            self.last_event_time = time.monotonic()") and "timer_lock" in lines[i-1]:
        pass
    else:
        new_lines.append(line)

with open("src/echo/watcher.py", "w") as f:
    f.writelines(new_lines)
