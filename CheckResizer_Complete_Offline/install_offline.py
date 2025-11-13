#!/usr/bin/env python3
"""
Offline installer - installs from pre-downloaded packages
"""
import subprocess
import sys
import os

def check_python():
    """Check if Python is available."""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor} found")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor} too old. Need 3.8+")
            return False
    except:
        print("❌ Python not found")
        return False

def install_packages():
    """Install packages from downloaded wheels."""
    print("📦 Installing dependencies from offline packages...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "--find-links", "python_packages",
            "--no-index",
            "streamlit", "opencv-python", "pillow", "numpy", 
            "scipy", "scikit-learn", "matplotlib"
        ], check=True)
        
        print("✅ All dependencies installed!")
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Installation failed")
        return False

if __name__ == "__main__":
    print("🚀 Check Resizer Offline Installer")
    print("=" * 40)
    
    if not check_python():
        print("\n❌ Python 3.8+ required but not found.")
        print("Please install Python first or use portable bundle.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if install_packages():
        print("\n🎉 Installation successful!")
        print("Run: python start_check_resizer.py")
    else:
        print("\n❌ Installation failed")
    
    input("Press Enter to exit...")
