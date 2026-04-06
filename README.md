# 📡 echo

> Lightweight file watcher. Trigger commands on changes. <5MB RAM.

## Features
- **🪶 Ultra Lightweight**: Uses native OS file observing capabilities via `watchdog` to consume virtually 0 resources.
- **⚡ Instant Feedback**: Re-runs your commands natively without spinning up complex pipelines.
- **💻 Cross Platform**: Built with Python + Rich bindings to operate seamlessly across OS boundaries.
- **⚡ Unblocked & Multi-threaded**: Runs execution in background threads so your file-watching event loop never pauses.
- **🔄 Smart Reloads**: Automatically terminates running processes if a new file change is detected. If processes become unresponsive or ignore termination signals, Echo forcefully escalates to `SIGKILL` after a short timeout to prevent deadlocks.
- **⏱️ Stable Debouncing**: Leverages monotonic clocks internally to guarantee reliable duration tracking, avoiding bugs related to system clock shifts and NTP syncs.
- **🚀 High-Throughput Safe**: Memoizes expensive file path ignoring evaluations to drastically reduce CPU overhead during burst operations (e.g., dependency installs).
- **⚙️ Crash Recovery**: Restarts automatically if encountering an unexpected system error.

## Quick Start
```bash
pip install echo-watcher
echo-watch --path ./src --cmd "pytest"
```

## 🤝 Contributing
Help us keep Echo as lightweight and precise as possible! 🦇
- 🐛 **Found a bug?** Open an issue to let us know.
- ✨ **Have a feature idea?** We are open to PRs! Just make sure not to bloat the watcher logic.
- 🎨 **Documentation tweaks?** Always welcome!

*Built by a Vibe Coder. Let the code compile itself.*
