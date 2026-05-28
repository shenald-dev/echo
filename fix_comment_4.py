with open("src/echo/watcher.py", "r") as f:
    content = f.read()

old_block = """        # Check for exact and wildcard ignore patterns matching cumulative prefix directories
        if self._has_compound_ignores and len(parts) > 1:
            prefix = parts[0]
            compound_exact_ignores = self.compound_exact_ignores"""

new_block = """        # Check for exact and wildcard ignore patterns matching cumulative prefix directories
        if self._has_compound_ignores and len(parts) > 1:
            prefix = parts[0]
            # Prefix for parts[0] is already evaluated via earlier exact match `isdisjoint()`
            # and wildcard matching, so we start accumulating from the second part.

            # Hot path optimization: hoist invariant truthiness and method lookup
            # (`match = ...match`) outside the inner accumulation loop.
            compound_exact_ignores = self.compound_exact_ignores"""

new_content = content.replace(old_block, new_block)

with open("src/echo/watcher.py", "w") as f:
    f.write(new_content)
