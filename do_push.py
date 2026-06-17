#!/usr/bin/env python
import subprocess
import os

os.chdir(r"d:\Carbon foot print")

# Stage all files
result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
print("Git add output:", result.stdout, result.stderr)

# Commit changes
result = subprocess.run(
    ["git", "commit", "-m", "Update EcoGuide: modular Flask app, integrated modules, cleaned app.py"],
    capture_output=True,
    text=True
)
print("Git commit output:", result.stdout, result.stderr)

# Push to remote
result = subprocess.run(["git", "push"], capture_output=True, text=True)
print("Git push output:", result.stdout, result.stderr)

if result.returncode == 0:
    print("\n✅ Successfully pushed changes to GitHub!")
else:
    print("\n❌ Push failed. Check the output above.")
