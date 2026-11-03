"""Command placeholder interpolation utilities for Echo."""

import os
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

    If the command template contains no braces, it is returned as-is without overhead.
    Unknown placeholders (like shell syntax '${VAR}' or regex '{1,3}') are safely preserved.
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
        "file": shlex.quote(norm_path),
        "path": shlex.quote(norm_path),
        "relpath": shlex.quote(rel_path),
        "basename": shlex.quote(basename),
        "stem": shlex.quote(stem),
        "dirname": shlex.quote(dirname),
        "ext": shlex.quote(ext),
        "event": shlex.quote(event_type),
    }

    result = command_template
    for key, val in mapping.items():
        placeholder = f"{{{key}}}"
        if placeholder in result:
            result = result.replace(placeholder, val)

    return result
