# Changelog

## [0.1.1] - 2025-02-21

### Changed
* **[Reliability]:** Implemented a timeout for process termination during file change events and graceful shutdowns. Echo now escalates to forceful termination (`SIGKILL`) to prevent thread deadlocks and application starvation if processes ignore standard termination signals (`SIGTERM`).
