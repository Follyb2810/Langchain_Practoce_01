import os
from pathlib import Path

print("Current directory:", os.getcwd())

# With pathlib
print("Current directory (pathlib):", Path.cwd())
# Using os
print(os.listdir("."))  # List everything in current dir

# Using pathlib
for item in Path(".").iterdir():
    print(item)
# os
os.makedirs("my_folder", exist_ok=True)

# pathlib
Path("my_folder").mkdir(parents=True, exist_ok=True)
# Open file for writing (creates if not exist, overwrites if it does)
with open("example.txt", "w") as f:
    f.write("Hello, World!\n")

# Append mode
with open("example.txt", "a") as f:
    f.write("This line is appended.\n")

# Read entire file
with open("example.txt", "r") as f:
    content = f.read()
print(content)

# Read line by line
with open("example.txt", "r") as f:
    for line in f:
        print("Line:", line.strip())

print(os.path.exists("example.txt"))  # True
print(Path("example.txt").exists())  # True

# Delete file
os.remove("example.txt")
Path("example.txt").unlink(missing_ok=True)

# Delete folder (only if empty)
os.rmdir("my_folder")

# Delete folder + all contents
import shutil

shutil.rmtree("my_folder", ignore_errors=True)

# Absolute path
print(os.path.abspath("example.txt"))

# Join paths safely
file_path = os.path.join("my_folder", "nested.txt")
print(file_path)

# pathlib way
print(Path("my_folder") / "nested.txt")

# 1. Create a folder
Path("notes").mkdir(exist_ok=True)

# 2. Write a file
with open("notes/todo.txt", "w") as f:
    f.write("Learn Python filesystem\n")
    f.write("Build a project\n")

# 3. Read it back
with open("notes/todo.txt", "r") as f:
    print(f.read())
