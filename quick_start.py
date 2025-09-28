#!/usr/bin/env python3
"""
Quick Start CPR Assistant
Bypasses dependency checking and runs directly
"""

import sys
import os

def main():
    """Quick start - just try to run the app"""
    print("Quick Start CPR Assistant")
    print("=" * 30)
    print("Attempting to start CPR Assistant...")
    print("If you get import errors, install dependencies first:")
    print("pip install opencv-python mediapipe numpy")
    print()
    
    try:
        # Try to import and run the app directly
        from simple_cpr_assistant import SimpleCPRAssistant
        print("✓ Dependencies found!")
        print("Starting CPR Assistant...")
        app = SimpleCPRAssistant()
        app.run()
        
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print()
        print("Please install the required packages:")
        print("pip install opencv-python mediapipe numpy")
        print()
        print("Or run:")
        print("pip install -r simple_requirements.txt")
        
    except Exception as e:
        print(f"✗ Error starting application: {e}")
        print("Please check your camera connection and try again.")

if __name__ == "__main__":
    main()
