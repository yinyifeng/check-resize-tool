#!/usr/bin/env python3
"""
Create portable Python bundle for Check Resizer Tool
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import zipfile

def create_portable_bundle():
    """Create a portable Python bundle with the application."""
    
    print("📦 Creating portable Python bundle...")
    
    bundle_dir = Path("CheckResizer_Portable")
    bundle_dir.mkdir(exist_ok=True)
    
    # Create directory structure
    (bundle_dir / "app").mkdir(exist_ok=True)
    (bundle_dir / "python").mkdir(exist_ok=True)
    
    # Copy application files
    app_files = [
        "check_resizer.py",
        "ui.py", 
        "launch_ui.py",
        "demo.py",
        "requirements.txt",
        "README.md",
        "TROUBLESHOOTING.md",
        "config.ini"
    ]
    
    for file in app_files:
        if Path(file).exists():
            shutil.copy2(file, bundle_dir / "app" / file)
    
    # Create launcher scripts
    create_launcher_scripts(bundle_dir)
    
    # Create installation script
    create_setup_script(bundle_dir)
    
    print(f"✅ Portable bundle created in '{bundle_dir}'")
    return bundle_dir

def create_launcher_scripts(bundle_dir):
    """Create launcher scripts for different platforms."""
    
    # Windows launcher
    windows_launcher = bundle_dir / "CheckResizer.bat"
    windows_launcher.write_text("""@echo off
cd /d "%~dp0"
echo Starting Check Resizer Tool...
echo ===============================

if not exist "python\\python.exe" (
    echo Python not found. Running setup...
    call setup.bat
)

echo Opening Check Resizer in your browser...
start "" "http://localhost:8501"
python\\python.exe -m streamlit run app\\ui.py --server.port 8501 --server.headless true
pause
""")
    
    # Unix/Linux/Mac launcher
    unix_launcher = bundle_dir / "CheckResizer.sh"
    unix_launcher.write_text("""#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Check Resizer Tool..."
echo "==============================="

if [ ! -f "python/bin/python" ]; then
    echo "Python environment not found. Running setup..."
    ./setup.sh
fi

echo "Opening Check Resizer in your browser..."
if command -v open >/dev/null 2>&1; then
    open "http://localhost:8501"  # macOS
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:8501"  # Linux
fi

python/bin/python -m streamlit run app/ui.py --server.port 8501 --server.headless true
read -p "Press any key to exit..."
""")
    unix_launcher.chmod(0o755)

def create_setup_script(bundle_dir):
    """Create setup scripts for first-time installation."""
    
    # Windows setup
    windows_setup = bundle_dir / "setup.bat"
    windows_setup.write_text("""@echo off
echo Setting up Check Resizer Tool...
echo ================================

echo Downloading Python (this may take a few minutes)...
curl -o python.zip "https://www.python.org/ftp/python/3.11.6/python-3.11.6-embed-amd64.zip"
powershell -command "Expand-Archive python.zip python"
del python.zip

echo Installing pip...
curl -o get-pip.py "https://bootstrap.pypa.io/get-pip.py"
python\\python.exe get-pip.py
del get-pip.py

echo Installing application dependencies...
python\\python.exe -m pip install -r app\\requirements.txt

echo Setup complete!
pause
""")
    
    # Unix setup
    unix_setup = bundle_dir / "setup.sh"
    unix_setup.write_text("""#!/bin/bash
echo "Setting up Check Resizer Tool..."
echo "================================"

# Create virtual environment
python3 -m venv python
source python/bin/activate

# Install dependencies
pip install -r app/requirements.txt

echo "Setup complete!"
read -p "Press any key to continue..."
""")
    unix_setup.chmod(0o755)

def create_offline_bundle():
    """Create completely offline bundle with pre-downloaded dependencies."""
    
    print("📦 Creating offline bundle with dependencies...")
    
    offline_dir = Path("CheckResizer_Offline")
    offline_dir.mkdir(exist_ok=True)
    
    # Download dependencies for offline installation
    deps_dir = offline_dir / "dependencies"
    deps_dir.mkdir(exist_ok=True)
    
    # Download wheel files for offline installation
    subprocess.run([
        sys.executable, "-m", "pip", "download",
        "-r", "requirements.txt",
        "-d", str(deps_dir)
    ])
    
    # Copy application
    app_dir = offline_dir / "app"
    shutil.copytree(".", app_dir, ignore=shutil.ignore_patterns(
        '__pycache__', '*.pyc', '.git*', 'dist', 'build', '*.egg-info',
        'CheckResizer_*', '.venv'
    ))
    
    # Create offline installer
    offline_installer = offline_dir / "install_offline.py"
    offline_installer.write_text("""#!/usr/bin/env python3
import subprocess
import sys
import os

def install_offline():
    print("Installing Check Resizer Tool (offline)...")
    
    # Install dependencies from downloaded wheels
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "--find-links", "dependencies",
        "--no-index",
        "-r", "app/requirements.txt"
    ])
    
    print("Installation complete!")
    print("Run 'python app/launch_ui.py' to start the application")

if __name__ == "__main__":
    install_offline()
""")
    
    print(f"✅ Offline bundle created in '{offline_dir}'")
    return offline_dir

if __name__ == "__main__":
    print("🚀 Check Resizer - Portable Bundle Creator")
    print("=" * 50)
    
    print("Choose bundle type:")
    print("1. Portable (requires internet for initial setup)")
    print("2. Offline (completely self-contained)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        bundle_dir = create_portable_bundle()
        print(f"\n✅ Portable bundle created!")
        print(f"📁 Location: {bundle_dir}")
        print("\n📋 To deploy:")
        print("1. Copy entire folder to target machine")
        print("2. Run CheckResizer.bat (Windows) or ./CheckResizer.sh (Unix)")
        print("3. First run will download Python and dependencies")
        
    elif choice == "2":
        bundle_dir = create_offline_bundle()
        print(f"\n✅ Offline bundle created!")
        print(f"📁 Location: {bundle_dir}")
        print("\n📋 To deploy:")
        print("1. Copy entire folder to target machine")
        print("2. Run 'python install_offline.py'")
        print("3. Then 'python app/launch_ui.py'")
        print("4. No internet required!")
    
    else:
        print("❌ Invalid choice")