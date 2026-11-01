<div align="center">
  <img src="assets/logo.png" alt="echo Logo" width="250" />
  
  <br/>

  <h1>📡 echo v1.0</h1>
  <p><b>High-Performance File Watcher & Task Runner for Developers</b></p>
  <i>Trigger commands on changes instantly. Multi-rule pipelines, dynamic placeholders, interactive controls. Consumes <5MB RAM.</i>

  <br/>
  
  [![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
  [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
  [![Version](https://img.shields.io/badge/Version-1.0.0-emerald.svg)](pyproject.toml)
  [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
</div>

---

## 📑 Table of Contents
- [🌟 Overview](#-overview)
- [✨ What's New in v1.0](#-whats-new-in-v10)
- [🚀 Enterprise Features](#-enterprise-features)
- [⚡ Quick Start Guide](#-quick-start-guide)
- [⌨️ Interactive Keyboard Controls (TUI)](#️-interactive-keyboard-controls-tui)
- [🎯 Multi-Rule Pipelines & Placeholders](#-multi-rule-pipelines--placeholders)
- [⚙️ Configuration Files](#️-configuration-files)
- [💻 Comprehensive CLI Reference](#-comprehensive-cli-reference)
- [🏎️ Performance & Benchmarks](#️-performance--benchmarks)
- [🤝 Contributing](#-contributing)

---

## 🌟 Overview

**echo** is an ultra-lightweight, high-performance file watcher and developer task runner built for the terminal. It leverages OS-native file observation (`inotify` on Linux, `FSEvents` on macOS, `ReadDirectoryChangesW` on Windows) to trigger your custom CLI commands the exact millisecond a file changes.

Whether you're compiling TypeScript, running unit test suites, rebuilding docs, or formatting codebases, **echo** delivers lightning-fast reloads without the bloat of heavy toolchains.

---

## ✨ What's New in v1.0

- 🎯 **Multi-Rule Pipeline Engine**: Map distinct file patterns to tailored tasks (e.g., `*.py` triggers `pytest {file}` while `*.ts` triggers `tsc --noEmit`).
- 🧩 **Dynamic Variable Placeholders**: Commands can interpolate changed file paths directly using `{file}`, `{relpath}`, `{basename}`, `{stem}`, `{dirname}`, `{ext}`, and `{event}`.
- ⚙️ **First-Class Configuration Support**: Zero-flag execution via `.echorc.json`, `echo.config.json`, or `pyproject.toml [tool.echo]`.
- ⌨️ **Interactive Terminal Hotkeys**: Live keyboard control (`r` to force re-run, `c` to clear screen, `p` to pause/resume, `h` for help, `q` to quit).
- ⏱️ **Flexible Debounce Intervals**: Configure debouncing with natural units (`--debounce 250ms`, `500`, or `1.5s`).
- 🧹 **Clean Terminal Mode (`--clear` / `-C`)**: Automatically clears the screen before each command execution for clean, distraction-free logs.
- 🚀 **Initial Run (`--initial` / `-i`)**: Executes configured commands immediately upon startup without waiting for the first file save.
- 🔔 **Terminal Bell Notifications (`--bell` / `-b`)**: Rings the terminal audio bell on command completion or failure.
- 📊 **Execution Telemetry**: Accurate execution duration timers (`⏱️ 42ms`), run sequence counters, and exit code indicators.
- 📦 **Dual CLI Commands**: Accessible as both `echo-watch` and `echo`.

---

## 🚀 Enterprise Features

- **🪶 Ultra Lightweight**: Consumes less than 5MB RAM with zero background bloat.
- **⚡ Instant Feedback**: Sub-millisecond dispatch through precomputed compiled ignore regexes and LRU hotpath caches.
- **💻 Cross Platform**: Seamless execution across Windows, macOS, and Linux with automatic ASCII transliteration fallback for non-UTF8 terminals.
- **🔄 Smart Reloads & Process Reaping**: Automatically terminates in-flight processes when new file changes arrive. Escalates to forceful process termination (`SIGKILL`) if commands become unresponsive.
- **⏱️ Monotonic Clock Debounce**: Guarantees rock-solid duration timing immune to NTP shifts and system clock adjustments.
- **🚀 Event-Driven Graceful Exit**: Unblocks timer threads instantly on exit signals (`SIGTERM`, `SIGINT`) with zero artificial sleep delays.

---

## ⚡ Quick Start Guide

### Installation

```bash
pip install echo-watcher
```

Or install from source:
```bash
git clone https://github.com/shenald-dev/echo.git
cd echo
pip install -e .
```

### Basic Usage

Watch the current directory and re-run your test suite on every save:
```bash
echo-watch --cmd "pytest"
```

Watch a specific path with instant initial run and screen clearing:
```bash
echo-watch --path ./src --cmd "pytest tests/" --initial --clear
```

---

## ⌨️ Interactive Keyboard Controls (TUI)

When running in an interactive terminal session, **echo** provides instant keyboard shortcuts:

| Key | Action | Description |
|:---:|:---|:---|
| <kbd>r</kbd> / <kbd>Enter</kbd> | **Force Re-Run** | Immediately executes the command without waiting for a file change. |
| <kbd>c</kbd> | **Clear Screen** | Clears the console screen cleanly. |
| <kbd>p</kbd> | **Pause / Resume** | Temporarily ignores file changes (useful during branch switches or git rebases). |
| <kbd>h</kbd> / <kbd>?</kbd> | **Hotkey Help** | Prints the hotkey cheat sheet. |
| <kbd>q</kbd> | **Clean Quit** | Safely terminates running child processes and shuts down Echo. |

*(To disable interactive mode in CI/CD or headless environments, pass `--no-interactive` / `-N`)*

---

## 🎯 Multi-Rule Pipelines & Placeholders

### Dynamic Placeholders

Inject details of the changed file directly into your commands:

| Placeholder | Description | Example Value |
|:---|:---|:---|
| `{file}` / `{path}` | Normalized path of the changed file | `src/controllers/auth.py` |
| `{relpath}` | Path relative to the watched base directory | `controllers/auth.py` |
| `{basename}` | File name with extension | `auth.py` |
| `{stem}` | File name without extension | `auth` |
| `{dirname}` | Directory containing the file | `src/controllers` |
| `{ext}` | File extension (without dot) | `py` |
| `{event}` | Event type | `modified`, `created`, `deleted`, `moved` |

Example:
```bash
echo-watch --cmd "ruff check {file}"
```

### Multiple Rules

Pass multiple rules via CLI using `--rule "pattern:command"`:
```bash
echo-watch \
  --rule "*.py:pytest {file}" \
  --rule "*.ts,*.tsx:npx tsc --noEmit" \
  --rule "*.scss:sass {file}:dist/{stem}.css"
```

---

## ⚙️ Configuration Files

Eliminate verbose CLI flags by defining your configuration in `.echorc.json`, `echo.config.json`, or `pyproject.toml`.

### Example: `.echorc.json`

```json
{
  "path": ".",
  "debounce": "300ms",
  "clear": true,
  "bell": false,
  "ignore": [
    "*.tmp",
    "dist/**",
    "build/**",
    ".cache/**"
  ],
  "rules": [
    {
      "patterns": ["*.py", "tests/*.py"],
      "cmd": "pytest {file}"
    },
    {
      "patterns": ["*.ts", "*.tsx"],
      "cmd": "npx tsc --noEmit"
    }
  ]
}
```

Now, simply run:
```bash
echo-watch
```

### Example: `pyproject.toml`

```toml
[tool.echo]
cmd = "pytest tests/ --cov=src"
debounce = 250
clear = true
ignore = ["*.tmp", "reports/*"]
```

---

## 💻 Comprehensive CLI Reference

```
usage: echo-watch [-h] [--path PATH] [--cmd CMD] [--ignore IGNORE]
                  [--debounce DEBOUNCE] [--rule RULE] [--config CONFIG]
                  [--clear] [--initial] [--bell] [--no-recursive]
                  [--no-interactive] [--version]
```

| Flag | Short | Description | Default |
|:---|:---:|:---|:---:|
| `--path` | `-p` | Directory to watch | `.` |
| `--cmd` | `-c` | Command to execute on change | None |
| `--rule` | | Multi-rule mapping (`pattern:cmd`) | `[]` |
| `--config` | | Explicit path to configuration file | Auto-discovered |
| `--debounce` | `-d` | Debounce duration (e.g. `250ms`, `500`, `0.5s`) | `250ms` |
| `--ignore` | | Comma-separated list of extra ignore patterns | `""` |
| `--clear` | `-C` | Clear terminal before executing command | `false` |
| `--initial` | `-i` | Execute command immediately upon startup | `false` |
| `--bell` | `-b` | Ring terminal audio bell upon command completion | `false` |
| `--no-recursive` | | Watch top-level directory only (no recursion) | `false` |
| `--no-interactive` | `-N` | Disable interactive keyboard shortcuts | `false` |
| `--version` | `-v` | Display version and exit | |
| `--help` | `-h` | Display usage manual and options | |

---

## 🏎️ Performance & Benchmarks

Echo is built for zero perceptible overhead:
- **Hot-Path Matching:** Pre-computes exact sets and compound regexes with an internal bounded LRU cache (evaluates 10,000 ignore checks in <0.05 seconds).
- **Lock-Free Event Ingestion:** Event dispatcher processes high-frequency bursts without thread contention.
- **Single Process / Thread-Safe:** Consistently uses <5MB RAM even when monitoring repos with 100,000+ files.

---

## 🤝 Contributing

We welcome contributions to make Echo faster, leaner, and more helpful!
- 🐛 **Found a bug?** Submit an issue on GitHub.
- 💡 **Have a feature idea?** Open a discussion or PR! Keep logic lean and focused.
- 🧪 **Tests:** Ensure all unit tests pass (`pytest --cov=src`) and linting is clean (`ruff check .`).

---

<div align="center">
  <sub>Built with ❤️ for pragmatic developers. Let the code compile itself.</sub>
</div>
