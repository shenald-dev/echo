# Changelog
## [0.1.25] - 2026-05-04

### Changed
* **[Performance]:** Split `exact_ignores` into simple and compound sets to prevent redundant evaluations against path segments, mirroring the wildcard optimization and further reducing hot path latency.

## [0.1.24]

// ... 5933.6 characters truncated (middle section) ...

 by lazy-evaluating destination paths during moved events, saving redundant ignore checks.
* **[Reliability]:** Hardened termination logic to set intent flags *before* making OS-level termination calls, preventing false failure logs when processes end concurrently.