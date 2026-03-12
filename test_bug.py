import time
import subprocess
import threading
import os

def modify_files():
    time.sleep(1)
    print("Modifying file 1...")
    os.system("echo '1' > test_dir/file1.txt")
    print("Modifying file 2...")
    os.system("echo '2' > test_dir/file2.txt")

os.makedirs("test_dir", exist_ok=True)
os.system("echo '0' > test_dir/file1.txt")
os.system("echo '0' > test_dir/file2.txt")

# Start the watcher
watcher = subprocess.Popen(["python", "src/echo/watcher.py", "--path", "test_dir", "--cmd", "sleep 3 && echo 'Command Ran!'"])

# Start modifying files in parallel
t = threading.Thread(target=modify_files)
t.start()

time.sleep(10)
watcher.terminate()
