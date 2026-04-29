def check(parts, exact_ignores):
    if len(parts) > 1:
        for i in range(len(parts)):
            prefix = parts[i]
            if prefix in exact_ignores:
                return True
            for part in parts[i+1:]:
                prefix = f"{prefix}/{part}"
                if prefix in exact_ignores:
                    return True
    return False

print(check(["src", "node_modules", "express", "index.js"], {"node_modules/express"}))
