# 📡 echo

> Lightweight file watcher. Trigger commands on changes. <5MB RAM.

## Features
- **🪶 Ultra Lightweight**: Uses native OS file observing capabilities via `watchdog` to consume virtually 0 resources.
- **⚡ Instant Feedback**: Re-runs your commands natively without spinning up complex pipelines.
- **💻 Cross Platform**: Built with Python + Rich bindings to operate seamlessly across OS boundaries.

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
