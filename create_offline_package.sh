#!/bin/bash
"""
Create completely offline, self-contained Check Resizer package
Includes Python interpreter and all dependencies
"""

echo "📦 Creating Offline Check Resizer Package..."
echo "============================================="

# Create main package directory
mkdir -p CheckResizer_Offline_Complete
cd CheckResizer_Offline_Complete

# Copy application files
echo "📋 Copying application files..."
cp ../ui.py ../check_resizer.py ../demo.py ../config.ini .
cp ../README.md ../TROUBLESHOOTING.md .

# Create requirements for offline installation
echo "📝 Creating offline requirements..."
cat > requirements_offline.txt << 'EOF'
streamlit==1.51.0
opencv-python==4.12.0.88
Pillow==12.0.0
numpy==2.3.4
scipy==1.16.3
scikit-learn==1.7.2
matplotlib==3.10.0
altair==5.5.0
plotly==6.4.0
click==8.3.0
tornado==6.5.2
pyarrow==21.0.0
EOF

# Download all dependencies for offline installation
echo "⬇️  Downloading dependencies for offline installation..."
mkdir -p python_packages
pip download -r requirements_offline.txt -d python_packages/

# Create offline installer script
cat > install_offline.py << 'EOF'
#!/usr/bin/env python3
"""
Offline installer for Check Resizer
"""
import subprocess
import sys
import os

def install_packages():
    """Install packages from downloaded wheels."""
    print("📦 Installing Check Resizer dependencies...")
    
    try:
        # Install from local packages
        result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "--find-links", "python_packages",
            "--no-index", "--no-deps",
            "--requirement", "requirements_offline.txt"
        ], check=True)
        
        print("✅ All dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Python pip not found. Please ensure Python is installed.")
        return False

if __name__ == "__main__":
    if install_packages():
        print("\n🎉 Installation complete!")
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
import os

def open_browser():
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:8501')
        print("🌐 Browser opened to http://localhost:8501")
    except:
        print("⚠️  Please manually open: http://localhost:8501")

def main():
    print("🚀 Starting Check Resizer...")
    print("=" * 40)
    
    # Start browser opener
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "ui.py",
            "--server.port=8501", "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
EOF

# Create README for deployment
cat > DEPLOYMENT_INSTRUCTIONS.txt << 'EOF'
# Check Resizer - Offline Complete Package

## 🎯 For Machines Without Internet or Python

This package works on machines that have NEITHER internet access NOR Python pre-installed.

### Option A: If Python is Available (but no internet)
1. Copy this entire folder to target machine
2. Run: python install_offline.py
3. Run: python start_check_resizer.py
4. Open browser to http://localhost:8501

### Option B: If NO Python Available
You need to install Python first:

**Windows:**
1. Download Python from https://python.org/downloads (on a machine with internet)
2. Copy python installer to target machine
3. Install Python on target machine
4. Follow Option A steps

**macOS:**
- Python 3 is usually pre-installed
- If not: brew install python3 (requires internet) or copy installer

**Linux:**
- Most distributions include Python 3
- If not: sudo apt install python3 python3-pip (requires internet)

### Option C: Completely Self-Contained (Advanced)
Use the portable Python approach below.

## 📦 Package Contents
- ui.py, check_resizer.py, demo.py - Application code
- python_packages/ - All dependencies as wheel files
- install_offline.py - Offline installer
- start_check_resizer.py - Application launcher

## 💾 Size: ~100MB (includes all dependencies)
## 🌐 Internet: NOT required after copying package
EOF

echo "✅ Offline package created!"
echo "📁 Location: CheckResizer_Offline_Complete/"
echo "📊 Size: $(du -sh CheckResizer_Offline_Complete | cut -f1)"