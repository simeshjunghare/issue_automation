import os
import sys
import subprocess
import platform

def install_playwright():
    try:
        # Install Playwright Python package
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright==1.48.0'], check=True)
        
        # Install Playwright browsers
        subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=True)
        
        # Install system dependencies (only on Linux)
        if platform.system() == 'Linux':
            subprocess.run([sys.executable, '-m', 'playwright', 'install-deps'], check=True)
            
        print("Successfully installed Playwright and its dependencies")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        print(f"Command that failed: {e.cmd}")
        print(f"Exit code: {e.returncode}")
        print(f"Output: {e.output}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    if not install_playwright():
        sys.exit(1)
