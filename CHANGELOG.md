# Changelog
        ## [0.1.25] - 2026-05-08

        ### Changed
        * **[Performance]:** Split `exact_ignores` into simple and compound frozensets to prevent redundant exact match evaluations against path segments, mirroring the wildcard optimization and further reducing latency in the hot path.

        ## [0.1.24] - 2026-05-02

        ### Changed
        * **[Performance]:** Split wildcard ignore patterns into simple and compound regexes to prevent redundant evaluations during path checking, 

        // ... 5575 characters truncated (middle section) ...

        ashes (e.g., `build/` becomes `build`), preventing bugs where valid directory ignore rules failed to match.

        ## [0.1.11] - 2026-04-17

        ### Changed
        * **[Performance]:** Optimized `on_any_event` by lazy-evaluating destination paths during moved events, saving redundant ignore checks.
        * **[Reliability]:** Hardened termination logic to set intent flags *before* making OS-level termination calls, preventing false failure logs when processes end concurrently.