import re
with open(".jules/bolt.md", "r") as f:
    content = f.read()

# Replace the conflict block with a merged version
conflict_block = """<<<<<<< HEAD
## 2026-05-15 — Hot Path Property Access Optimization

Learning:
Inside the high-frequency event loop (`on_any_event`) of the file watcher, relying on `getattr(event, 'event_type', '')` and `getattr(event, 'src_path', None)` introduces unnecessary function call overhead. Since `event_type` and `src_path` are guaranteed attributes on `watchdog.events.FileSystemEvent`, direct attribute access is significantly faster. Similarly, recalculating the `len()` of prefix strings inside the string slicing operations in `_is_ignored_impl` occurs redundantly for every ignored file path check. Furthermore, loop invariant checks like `if self.compound_wildcard_regex:` inside hot-path iterations can be safely hoisted using loop unswitching to eliminate branch evaluation on every iteration.

Action:
Replaced dynamic `getattr()` calls with direct attribute access (`event.event_type`, `event.src_path`) where safe. Pre-calculated and stored base path lengths (`self._abs_base_path_len`, `self._base_prefix_len`) during instantiation to optimize slicing. Hoisted loop invariant truthiness evaluations for regex objects out of the iteration body to streamline directory path filtering.
=======
## 2026-05-16 — Generator Expression Overhead in Hot Paths

Learning:
In high-frequency Python hot paths (like checking path parts against a regex), using `any()` with a generator expression (e.g., `any(match(p) for p in parts)`) introduces generator overhead that makes it slower than a simple, explicit `for` loop. Additionally, redundant property accesses (`getattr`) and redundant loop-invariant truthiness checks (`if self.compound_wildcard_regex:`) inside loops cause measurable performance regressions.

Action:
Prefer explicit `for` loops with early returns over `any()` generators in hot paths. Lift loop-invariant checks and expensive builtins (like `len()`) outside of tight loops. Use direct attribute access over `getattr` when the attribute's existence is guaranteed.
>>>>>>> origin/main"""

merged_block = """## 2026-05-15 — Hot Path Property Access Optimization

Learning:
Inside the high-frequency event loop (`on_any_event`) of the file watcher, relying on `getattr(event, 'event_type', '')` and `getattr(event, 'src_path', None)` introduces unnecessary function call overhead. Since `event_type` and `src_path` are guaranteed attributes on `watchdog.events.FileSystemEvent`, direct attribute access is significantly faster. Similarly, recalculating the `len()` of prefix strings inside the string slicing operations in `_is_ignored_impl` occurs redundantly for every ignored file path check. Furthermore, loop invariant checks like `if self.compound_wildcard_regex:` inside hot-path iterations can be safely hoisted using loop unswitching to eliminate branch evaluation on every iteration.

Action:
Replaced dynamic `getattr()` calls with direct attribute access (`event.event_type`, `event.src_path`) where safe. Pre-calculated and stored base path lengths (`self._abs_base_path_len`, `self._base_prefix_len`) during instantiation to optimize slicing. Hoisted loop invariant truthiness evaluations for regex objects out of the iteration body to streamline directory path filtering.

## 2026-05-16 — Generator Expression Overhead in Hot Paths

Learning:
In high-frequency Python hot paths (like checking path parts against a regex), using `any()` with a generator expression (e.g., `any(match(p) for p in parts)`) introduces generator overhead that makes it slower than a simple, explicit `for` loop. Additionally, redundant property accesses (`getattr`) and redundant loop-invariant truthiness checks (`if self.compound_wildcard_regex:`) inside loops cause measurable performance regressions.

Action:
Prefer explicit `for` loops with early returns over `any()` generators in hot paths. Lift loop-invariant checks and expensive builtins (like `len()`) outside of tight loops. Use direct attribute access over `getattr` when the attribute's existence is guaranteed."""

content = content.replace(conflict_block, merged_block)

with open(".jules/bolt.md", "w") as f:
    f.write(content)
