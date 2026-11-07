"""Command placeholder interpolation utilities for Echo."""

import os
import re
import shlex

from pathlib import Path


def interpolate_command(
    command_template: str,
    event_path: str,
    base_path: str = ".",
    event_type: str = "modified",
) -> str:
    """Safely interpolate file-path placeholders into a command string.

    Supported placeholders:
      - {file} or {path}: Normalized path to the changed file.
      - {relpath}: Path relative to base_path or current working directory.
      - {basename}: File name with extension (e.g., 'main.py').
      - {stem}: File name without extension (e.g., 'main').
      - {dirname}: Directory containing the file.
      - {ext}: File extension without leading dot (e.g., 'py').
      - {event}: Event type ('modified', 'created', 'deleted', 'moved').

    If the command template contains no braces, it is returned as-is
    without overhead. Unknown placeholders (like shell syntax '${VAR}'
    or regex '{1,3}') are safely preserved.
    """
    if "{" not in command_template:
        return command_template

    norm_path = os.path.normpath(event_path)
    try:
        rel_path = os.path.relpath(norm_path, base_path)
    except ValueError:
        rel_path = norm_path

    p = Path(norm_path)
    basename = p.name
    stem = p.stem
    dirname = str(p.parent)
    ext = p.suffix.lstrip(".")

    mapping = {
        "file": norm_path,
        "path": norm_path,
        "relpath": rel_path,
        "basename": basename,
        "stem": stem,
        "dirname": dirname,
        "ext": ext,
        "event": event_type,
    }

    def replacer(match):
        left_quote = match.group(1)
        key = match.group(2)
        right_quote = match.group(3)
        if key in mapping:
            # Must return str because mapping values might not be strings
            val = str(mapping[key])
            quoted_val = shlex.quote(val)
            if left_quote and right_quote and left_quote == right_quote:
                return quoted_val
            return left_quote + quoted_val + right_quote
        return match.group(0)

    pattern = r'([\'"]?)\{([a-zA-Z_][a-zA-Z0-9_]*)\}([\'"]?)'
    return re.sub(pattern, replacer, command_template)
