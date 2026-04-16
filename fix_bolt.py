with open('.jules/bolt.md', 'r') as f:
    lines = f.readlines()

new_lines = []
in_conflict = False
for line in lines:
    if line.startswith('<<<<<<< HEAD'):
        in_conflict = True
    elif line.startswith('======='):
        pass
    elif line.startswith('>>>>>>> origin/main'):
        in_conflict = False
        pass
    else:
        new_lines.append(line)

with open('.jules/bolt.md', 'w') as f:
    f.writelines(new_lines)
