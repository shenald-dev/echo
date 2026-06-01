<div align="center">
  <img src="assets/logo.png" alt="echo Logo" width="250" />
  
  <br/>

  <h1>📡 echo</h1>
  <p><b>Ultra-Lightweight File Watcher</b></p>
  <i>Trigger commands on changes instantly. Consumes <5MB RAM.</i>

  <br/>
  
  [![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
  [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

---

## 📑 Table of Contents
- [🌟 Overview](#-overview)
- [🚀 Enterprise Features](#-enterprise-features)
- [⚡ Quick Start Guide](#-quick-start-guide)
- [💻 Comprehensive Usage](#-comprehensive-usage)
- [🤝 Contributing](#-contributing)

---

## 🌟 Overview

**echo** is an ultra-lightweight, high-performance file watcher built for the terminal. It leverages operating system-native file observation to trigger your custom CLI commands the exact millisecond a file changes, making it the ultimate local development companion.

---

## 🚀 Enterprise Features

- **🪶 Ultra Lightweight**: Uses native OS file capabilities via `watchdog` to consume virtually 0 resources (<5MB RAM).
- **⚡ Instant Feedback**: Re-runs your commands natively without spinning up complex wrapper pipelines.
- **💻 Cross Platform**: Built with Python + Rich bindings to operate seamlessly across Windows, MacOS, and Linux.
- **⚡ Unblocked & Multi-threaded**: Runs execution in background threads so your file-watching event loop never pauses. Removed lock contention overhead during event evaluation for higher throughput.
- **🔄 Smart Reloads**: Automatically terminates running processes if a new file change is detected. If processes become unresponsive or ignore termination signals, Echo forcefully escalates to `SIGKILL` after a short timeout to prevent deadlocks.
- **⏱️ Stable Debouncing**: Leverages monotonic clocks internally to guarantee reliable duration tracking, avoiding bugs related to system clock shifts and NTP syncs.
- **🚀 Fast Event-Driven Shutdown**: Uses thread-safe events to instantly unblock background timers during exit, eliminating artificial sleep latency and ensuring clean shutdowns.
- **⚙️ Crash Recovery**: Restarts automatically if encountering an unexpected system error.

---

## ⚡ Quick Start Guide

### Installation

```bash
pip install echo-watcher
```

---

## 💻 Comprehensive Usage

### Watch a Directory

Tell echo what directory to watch, and what command to execute on change:
```bash
echo-watch --path ./src --cmd "pytest"
```

### Advanced Usage

You can fine-tune the debouncing and recursive behavior:
```bash
echo-watch --path ./app --cmd "npm run build" --debounce 500 --no-recursive
```

---

## 🤝 Contributing
Help us keep Echo as lightweight and precise as possible! 🦇
- 🐛 **Found a bug?** Open an issue to let us know.
- ✨ **Have a feature idea?** We are open to PRs! Just make sure not to bloat the watcher logic.
- 🎨 **Documentation tweaks?** Always welcome!

---
> *Built by a Vibe Coder. Let the code compile itself.*
