#!/usr/bin/env python3
"""
Simple CPR Assistant Launcher
Launcher for the simplified CPR Assistant (no audio, no LLM)
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['cv2', 'mediapipe', 'numpy']
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'mediapipe':
                import mediapipe
            elif package == 'numpy':
                import numpy
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'simple_requirements.txt'])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main launcher function"""
    print("Simple CPR Assistant Launcher")
    print("=" * 35)
    
    # Check dependencies
    print("Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Installing dependencies...")
        
        if not install_dependencies():
            print("Failed to install dependencies. Please install manually:")
            print("pip install -r simple_requirements.txt")
            return
        
        # Check again after installation
        missing = check_dependencies()
        if missing:
            print(f"Still missing: {', '.join(missing)}")
            print("Please install manually and try again.")
            return
    
    print("All dependencies found!")
    print("Starting Simple CPR Assistant...")
    
    # Launch the main application
    try:
        from simple_cpr_assistant import SimpleCPRAssistant
        app = SimpleCPRAssistant()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start Simple CPR Assistant: {e}")

if __name__ == "__main__":
    main()
