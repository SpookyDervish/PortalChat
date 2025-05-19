from ui.app import Portal
import subprocess, sys


if __name__ == "__main__":
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e}")
        sys.exit(1)
    app = Portal()
    app.run()