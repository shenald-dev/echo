# Changelog

          ## [0.1.32] - 2026-05-29

          ### Performance
          - Optimized `_is_ignored` hot path by bypassing `dest_path` extraction and path splitting for common scenarios, reducing overhead during burst file events.

          ## [0.1.31] - 2026-05-28

          ### Changed
          * **[Quality]:** Assured the optimization to hoist regex variables in the ignore loop. Resolved stat