#!/usr/bin/env python3
"""
Build script to create standalone executable for Check Resizer Tool
"""

import subprocess
import sys
import os
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        subprocess.check_output([sys.executable, "-c", "import PyInstaller"], stderr=subprocess.STDOUT)
        print("✅ PyInstaller already installed")
    except subprocess.CalledProcessError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def build_executable():
    """Build the standalone executable."""
    print("🔨 Building standalone executable...")
    
    # PyInstaller command to create executable
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window (optional)
        "--name=CheckResizer",
        "--icon=check_icon.ico",  # Optional icon
        "--add-data=requirements.txt:.",
        "--hidden-import=streamlit",
        "--hidden-import=cv2",
        "--hidden-import=numpy",
        "--hidden-import=PIL",
        "--hidden-import=scipy",
        "--hidden-import=sklearn",
        "--collect-all=streamlit",
        "launch_ui.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ Executable built successfully!")
        print("📁 Check the 'dist' folder for the executable")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

def create_distribution_package():
    """Create a complete distribution package."""
    print("📦 Creating distribution package...")
    
    dist_dir = Path("distribution")
    dist_dir.mkdir(exist_ok=True)
    
    # Copy necessary files
    files_to_copy = [
        "README.md",
        "TROUBLESHOOTING.md",
        "config.ini",
        "requirements.txt"
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            import shutil
            shutil.copy2(file, dist_dir / file)
    
    # Create startup script
    startup_script = dist_dir / "run_check_resizer.bat"  # Windows
    startup_script.write_text("""@echo off
echo Starting Check Resizer Tool...
CheckResizer.exe
pause
""")
    
    startup_script_unix = dist_dir / "run_check_resizer.sh"  # Unix/Linux/Mac
    startup_script_unix.write_text("""#!/bin/bash
echo "Starting Check Resizer Tool..."
./CheckResizer
read -p "Press any key to continue..."
""")
    startup_script_unix.chmod(0o755)
    
    print("✅ Distribution package created in 'distribution' folder")

if __name__ == "__main__":
    print("🚀 Check Resizer - Standalone Build Tool")
    print("=" * 50)
    
    install_pyinstaller()
    
    if build_executable():
        create_distribution_package()
        
        print("\n🎉 Build Complete!")
        print("=" * 50)
        print("📁 Executable location: dist/CheckResizer.exe (or CheckResizer)")
        print("📦 Distribution package: distribution/")
        print("\n💡 To deploy:")
        print("1. Copy the 'dist' folder to target machine")
        print("2. Run CheckResizer.exe (Windows) or ./CheckResizer (Unix)")
        print("3. No Python installation required on target machine!")