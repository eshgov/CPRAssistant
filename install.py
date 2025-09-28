#!/usr/bin/env python3
"""
Simple Installation Script
Just installs the dependencies without checking
"""

import subprocess
import sys

def main():
    print("Installing CPR Assistant Dependencies")
    print("=" * 40)
    
    packages = [
        "opencv-python",
        "mediapipe", 
        "numpy"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")
    
    print("\nInstallation complete!")
    print("Now you can run: python direct_run.py")

if __name__ == "__main__":
    main()
