import subprocess, sys

# auto install dependencies
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError as e:
    print(f"Installation failed: {e}")
    sys.exit(1)

from ui.app import Portal


if __name__ == "__main__":
    app = Portal()
    app.run()