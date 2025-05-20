import subprocess
import sys
from pathlib import Path

req_file = Path("requirements.txt")

if not req_file.exists():
    print("❌ requirements.txt not found.")
    sys.exit(1)

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
    print("✅ All requirements installed successfully.")
except subprocess.CalledProcessError as e:
    print("❌ Pip install failed:", e)
    sys.exit(1)
