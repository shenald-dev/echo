@@ -1,4 +1,19 @@
 # Changelog
+## [0.1.24] - 2026-05-02
+
+### Changed
+* **[Performance]:** Split wildcard ignore patterns into simple and compound regexes to prevent redundant evaluations during path checking, improving file event performance.
+
+
+## [0.1.24] - 2026-04-30
+
+### Changed
+* **[Reliability]:** Fixed a bug in the ignore pattern matching where deep subpaths (e.g. `node_modules/express`) were not correctly ignored if they were not the starting prefix.
+
+## [0.1.23] - 2026-04-30
+
+### Changed
+* **[Performance]:** Optimized ignore file filtering in hot paths by fast-tracking common relative paths and avoiding compound loop iterations when unnecessary, significantly reducing CPU cycles on burst saves.
 
 ## [0.1.22] - 2026-04-29