with open("src/echo/watcher.py", "r") as f:
    content = f.read()

conflict = """<<<<<<< HEAD
            if self.compound_wildcard_regex:
                match = self.compound_wildcard_regex.match
                for part in parts[1:]:
                    prefix = f"{prefix}/{part}"
                    if prefix in self.compound_exact_ignores:
                        return True
                    if match(prefix):
                        return True
            else:
                for part in parts[1:]:
                    prefix = f"{prefix}/{part}"
                    if prefix in self.compound_exact_ignores:
                        return True
=======
            match = self.compound_wildcard_regex.match if self.compound_wildcard_regex else None
            for part in parts[1:]:
                prefix = f"{prefix}/{part}"
                if prefix in self.compound_exact_ignores:
                    return True
                if match and match(prefix):
                    return True
>>>>>>> origin/main"""

resolution = """            if self.compound_wildcard_regex:
                match = self.compound_wildcard_regex.match
                for part in parts[1:]:
                    prefix = f"{prefix}/{part}"
                    if prefix in self.compound_exact_ignores:
                        return True
                    if match(prefix):
                        return True
            else:
                for part in parts[1:]:
                    prefix = f"{prefix}/{part}"
                    if prefix in self.compound_exact_ignores:
                        return True"""

new_content = content.replace(conflict, resolution)

with open("src/echo/watcher.py", "w") as f:
    f.write(new_content)

print("Conflict resolved!")
