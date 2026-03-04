# Echo

> Quiet, efficient file system monitoring that stays out of your way.

Echo watches your files and directories, triggering actions when changes occur. Perfect for development workflows and automation.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
[![CI](https://github.com/shenald-dev/echo/actions/workflows/ci.yml/badge.svg)](https://github.com/shenald-dev/echo/actions/workflows/ci.yml)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- Recursive directory watching
- Pattern-based filtering
- Low memory footprint
- Simple CLI and Python API
- Cross-platform

## Installation

```bash
pip install echo-monitor
```

## Quick Example

```bash
echo watch ./src --pattern "*.py" --command "pytest"
```

## Why Echo?

Most file watchers are either too complex or not flexible enough. Echo keeps it simple: watch, filter, act.

## License

MIT © Shenald
