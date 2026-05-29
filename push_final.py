import subprocess
try:
    subprocess.run(["git", "push", "origin", "bolt-prime-optimization-11539132730487664538", "--force"], check=True)
except Exception as e:
    print(f"Failed to push: {e}")
