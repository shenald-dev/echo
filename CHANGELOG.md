# Changelog
## [0.1.26] - 2026-05-10
### Performance
- Optimized wildcard ignore checking by hoisting conditions and method lookups out of the path accumulation loop.

## [0.1.25] - 2026-05-04
### Changed
* **[Performance]:** Split `exact_ignores` into simple and compound sets to prevent redundant evaluations against path segments, mirroring the wildcard optimization and further reducing hot path latency.

## [0.1.24] - 2026-05-02
### Changed
* **[Performance]:** Split wildcard ignore patterns into simple and compound regexes to prevent redundant evaluations during path checking, improving file event performance.

## [0.1.23] - 2026-04-30
// ... 5453.8 characters truncated (middle section) ...
 **Fix:** Normalize ignore patterns by stripping trailing slashes (e.g., `build/` becomes `build`), preventing bugs where valid directory ignore rules failed to match.

## [0.1.11] - 2026-04-17
### Changed
* **[Performance]:** Optimized `on_any_event` by lazy-e