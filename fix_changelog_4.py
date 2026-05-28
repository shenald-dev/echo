with open("CHANGELOG.md", "r") as f:
    changelog = f.read()

new_changelog_entry = """## [0.1.27] - 2026-05-21

### Changed
* **[Performance]:** Assured the event loop lock contention optimizations, validating thread safety and structure without introducing new regressions.

"""

if "## [0.1.27]" not in changelog:
    changelog = changelog.replace("## [0.1.26]", new_changelog_entry + "## [0.1.26]")
    with open("CHANGELOG.md", "w") as f:
        f.write(changelog)
