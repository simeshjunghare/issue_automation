import os
import sys
import subprocess

def install_playwright():
    try:
        # Install Playwright browsers
        subprocess.run(['playwright', 'install', 'chromium'], check=True)
        subprocess.run(['playwright', 'install-deps'], check=True)
        print("Successfully installed Playwright browsers and dependencies")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Playwright: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_playwright()
