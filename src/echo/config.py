"""Configuration loader and schema validator for Echo."""

import json
from pathlib import Path
from typing import Any

DEFAULT_DEBOUNCE_SEC = 0.25
DEFAULT_IGNORES = [
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    ".venv",
    "venv",
]


def parse_debounce(value: Any) -> float:
    """Parse a debounce duration string or number into seconds.

    Supports:
      - 250 -> 0.25s (integers/floats >= 10 are treated as milliseconds)
      - 0.5 -> 0.5s (numbers < 10 are treated as seconds)
      - "300ms" -> 0.3s
      - "1.5s" -> 1.5s
      - "500" -> 0.5s
    """
    if value is None:
        return DEFAULT_DEBOUNCE_SEC

    if isinstance(value, (int, float)):
        if value < 0:
            return DEFAULT_DEBOUNCE_SEC
        if value >= 10:
            return float(value) / 1000.0
        return float(value)

    if isinstance(value, str):
        v = value.strip().lower()
        if v.endswith("ms"):
            try:
                ms = float(v[:-2].strip())
                return max(0.0, ms / 1000.0)
            except ValueError:
                return DEFAULT_DEBOUNCE_SEC
        if v.endswith("s"):
            try:
                sec = float(v[:-1].strip())
                return max(0.0, sec)
            except ValueError:
                return DEFAULT_DEBOUNCE_SEC
        try:
            num = float(v)
            if num >= 10:
                return num / 1000.0
            return max(0.0, num)
        except ValueError:
            return DEFAULT_DEBOUNCE_SEC

    return DEFAULT_DEBOUNCE_SEC


def _load_json_file(file_path: Path) -> dict[str, Any]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _load_pyproject_toml(file_path: Path) -> dict[str, Any]:
    try:
        # Use standard library tomllib if on Python 3.11+, else try tomli
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                return {}

        with open(file_path, "rb") as f:
            data = tomllib.load(f)
            if isinstance(data, dict):
                tool = data.get("tool", {})
                if isinstance(tool, dict) and "echo" in tool:
                    echo_config = tool["echo"]
                    if isinstance(echo_config, dict):
                        return echo_config
    except Exception:
        pass
    return {}


def find_config_file(explicit_path: str | None = None, search_dir: str = ".") -> Path | None:
    """Locate an explicit or auto-discovered configuration file."""
    if explicit_path:
        p = Path(explicit_path)
        if p.is_file():
            return p
        return None

    candidates = [
        ".echorc.json",
        ".echorc",
        "echo.config.json",
        ".echo.json",
        "pyproject.toml",
    ]

    base = Path(search_dir).resolve()
    for candidate in candidates:
        target = base / candidate
        if target.is_file():
            return target

    return None


def load_config(explicit_path: str | None = None, search_dir: str = ".") -> dict[str, Any]:
    """Load configuration from file, normalizing default fields."""
    config_file = find_config_file(explicit_path, search_dir)
    raw_data: dict[str, Any] = {}

    if config_file:
        if config_file.name == "pyproject.toml":
            raw_data = _load_pyproject_toml(config_file)
        else:
            raw_data = _load_json_file(config_file)

    normalized: dict[str, Any] = {
        "cmd": raw_data.get("cmd"),
        "path": raw_data.get("path", "."),
        "ignore": raw_data.get("ignore", []),
        "debounce_sec": parse_debounce(raw_data.get("debounce")),
        "clear": bool(raw_data.get("clear", False)),
        "bell": bool(raw_data.get("bell", False)),
        "recursive": bool(raw_data.get("recursive", True)),
        "rules": raw_data.get("rules", []),
        "_loaded_from": str(config_file) if config_file else None,
    }

    # Ensure ignore is a list of strings
    if isinstance(normalized["ignore"], str):
        normalized["ignore"] = [p.strip() for p in normalized["ignore"].split(",") if p.strip()]
    elif not isinstance(normalized["ignore"], list):
        normalized["ignore"] = []

    return normalized
