#!/usr/bin/env python3
"""
Improved CPR Assistant Launcher
Launcher for the improved CPR Assistant with better BPM calculation and cloud upload
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def main():
    """Main launcher function"""
    print("Improved CPR Assistant Launcher")
    print("=" * 40)
    print("Features:")
    print("• Improved BPM calculation (last 4 beats)")
    print("• Better compression detection")
    print("• Cloud upload for model training")
    print("• Face blurring for privacy")
    print()
    
    try:
        # Try to import and run the app directly
        from improved_cpr_assistant import ImprovedCPRAssistant
        print("✓ Dependencies found!")
        print("Starting Improved CPR Assistant...")
        app = ImprovedCPRAssistant()
        app.run()
        
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print()
        print("Please install the required packages:")
        print("pip install opencv-python mediapipe numpy requests")
        print()
        print("Or run:")
        print("pip install -r improved_requirements.txt")
        
    except Exception as e:
        print(f"✗ Error starting application: {e}")
        print("Please check your camera connection and try again.")

if __name__ == "__main__":
    main()
