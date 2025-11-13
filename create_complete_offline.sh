#!/bin/bash
"""
Create completely self-contained package with Python included
For machines with NO Python and NO internet
"""

echo "📦 Creating Self-Contained Check Resizer Package..."
echo "=================================================="

# Create main package directory
mkdir -p CheckResizer_Complete_Offline
cd CheckResizer_Complete_Offline

echo "📋 Step 1: Copying application files..."
cp ../ui.py ../check_resizer.py ../demo.py ../config.ini .
cp ../README.md ../TROUBLESHOOTING.md .

echo "📦 Step 2: Download Python dependencies offline..."
mkdir -p python_packages
pip download streamlit opencv-python pillow numpy scipy scikit-learn matplotlib -d python_packages/

echo "📝 Step 3: Creating deployment instructions..."

# For Windows - Python embeddable
cat > DEPLOY_WINDOWS.txt << 'EOF'
# Windows Deployment (No Python Required)

## Step 1: Download Python Embeddable (on internet machine)
1. Go to https://www.python.org/downloads/windows/
2. Download "Windows embeddable package" for Python 3.11
3. Example: python-3.11.6-embed-amd64.zip

## Step 2: Prepare Package
1. Create folder: CheckResizer_Windows/
2. Extract python-embed.zip to: CheckResizer_Windows/python/
3. Copy this entire CheckResizer_Complete_Offline/ to CheckResizer_Windows/app/
4. Download get-pip.py to CheckResizer_Windows/

## Step 3: Create Installer (run on target machine)
@echo off
cd /d "%~dp0"
echo Installing Check Resizer...

REM Install pip
python\python.exe get-pip.py

REM Install dependencies from local packages
python\python.exe -m pip install --find-links app\python_packages --no-index -r app\requirements_offline.txt

echo Installation complete!
pause

## Step 4: Create Launcher
@echo off
cd /d "%~dp0"
echo Starting Check Resizer...
start "" "http://localhost:8501"
python\python.exe -m streamlit run app\ui.py --server.port 8501
pause

## Final Package Size: ~100MB (Python + App + Dependencies)
EOF

# For macOS - Portable Python approach  
cat > DEPLOY_MACOS.txt << 'EOF'
# macOS Deployment (No Python Required)

## Option A: Use Existing Python
Most macOS systems have Python 3 built-in:
1. Copy CheckResizer_Complete_Offline/ to target Mac
2. Run: python3 install_offline.py
3. Run: python3 start_check_resizer.py

## Option B: Portable Python (if no Python available)
1. Create conda environment on internet machine:
   conda create -n portable python=3.11
   conda activate portable
   pip install streamlit opencv-python pillow numpy scipy scikit-learn matplotlib
   conda install conda-pack
   conda-pack -n portable -o portable_python.tar.gz

2. Copy to target machine and extract:
   tar -xzf portable_python.tar.gz
   source bin/activate
   conda-unpack

3. Run application:
   ./bin/python start_check_resizer.py

## Final Package Size: ~150MB
EOF

# For Linux - AppImage or Static Python
cat > DEPLOY_LINUX.txt << 'EOF'
# Linux Deployment (No Python Required)

## Option A: Static Python Build
1. Download Python static build from:
   https://github.com/indygreg/python-build-standalone
2. Extract to target machine
3. Install dependencies and run app

## Option B: Use System Python
Most Linux distributions include Python 3:
1. Copy CheckResizer_Complete_Offline/ to target
2. Run: python3 install_offline.py  
3. Run: python3 start_check_resizer.py

## Option C: Docker (if Docker available)
1. Build container with Python + app
2. Export as .tar file
3. Load and run on target machine

## Final Package Size: ~120MB
EOF

# Create universal offline installer
cat > install_offline.py << 'EOF'
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
EOF

# Create simple launcher
cat > start_check_resizer.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import sys
import webbrowser
import time
import threading

def open_browser():
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:8501')
        print("🌐 Opened http://localhost:8501")
    except:
        print("⚠️  Please open: http://localhost:8501")

def main():
    print("🚀 Starting Check Resizer...")
    print("=" * 30)
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "ui.py",
            "--server.port=8501", "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter...")

if __name__ == "__main__":
    main()
EOF

# Create requirements file
cat > requirements_offline.txt << 'EOF'
streamlit
opencv-python  
pillow
numpy
scipy
scikit-learn
matplotlib
EOF

echo ""
echo "✅ Complete offline package created!"
echo "📁 Location: CheckResizer_Complete_Offline/"
echo ""
echo "📋 Contents:"
echo "  - Application files (ui.py, etc.)"
echo "  - Pre-downloaded Python packages"
echo "  - Platform-specific deployment guides"
echo "  - Offline installer script"
echo ""
echo "📊 Package size: $(du -sh . 2>/dev/null | cut -f1)"
echo ""
echo "🎯 For target machines:"
echo "  1. Copy entire folder to target machine"
echo "  2. Follow DEPLOY_[PLATFORM].txt instructions"
echo "  3. Run install_offline.py then start_check_resizer.py"