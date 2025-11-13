#!/bin/bash
"""
Create truly portable Check Resizer with embedded Python
Works on machines with NO Python installation
"""

echo "🚀 Creating Portable Python Bundle..."
echo "====================================="

# Create portable directory
mkdir -p CheckResizer_Portable_Python
cd CheckResizer_Portable_Python

# For macOS - use Python framework approach
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📦 Creating macOS portable bundle..."
    
    # Copy current Python environment
    mkdir -p python_runtime
    
    # Copy Python executable and libraries (simplified approach)
    echo "⚠️  For full portability on macOS:"
    echo "1. Use PyInstaller (as attempted earlier)"
    echo "2. Or use conda-pack to create portable environment"
    echo "3. Or use Docker for true isolation"
    
    cat > create_conda_portable.sh << 'EOF'
#!/bin/bash
# Install conda-pack for portable environments
pip install conda-pack

# Create a new conda environment
conda create -n checkresizer python=3.11 -y
conda activate checkresizer

# Install dependencies
pip install streamlit opencv-python pillow numpy scipy scikit-learn matplotlib

# Pack the environment
conda-pack -n checkresizer -o checkresizer_env.tar.gz

# Extract to portable location
mkdir -p portable_python
cd portable_python
tar -xzf ../checkresizer_env.tar.gz

# Fix conda-pack environment
source bin/activate
conda-unpack

echo "✅ Portable Python environment created!"
EOF
    
fi

# For Linux - use AppImage approach
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 For Linux: Consider AppImage approach"
    
    cat > create_appimage.sh << 'EOF'
#!/bin/bash
# Download Python AppImage
wget https://github.com/niess/python-appimage/releases/download/python3.11/python3.11.6-cp311-cp311-linux_x86_64.AppImage
chmod +x python3.11.6-cp311-cp311-linux_x86_64.AppImage

# Extract AppImage
./python3.11.6-cp311-cp311-linux_x86_64.AppImage --appimage-extract

# Install dependencies in extracted Python
squashfs-root/AppRun -m pip install streamlit opencv-python pillow numpy scipy scikit-learn matplotlib

# Create launcher script
cat > run_checkresizer.sh << 'INNER_EOF'
#!/bin/bash
cd "$(dirname "$0")"
./squashfs-root/AppRun start_check_resizer.py
INNER_EOF
chmod +x run_checkresizer.sh

echo "✅ Portable Linux bundle created!"
EOF

fi

# For Windows - use embeddable Python
cat > create_windows_portable.bat << 'EOF'
@echo off
echo Creating Windows Portable Bundle...

REM Download Python embeddable distribution
echo Downloading Python embeddable...
curl -o python-embed.zip "https://www.python.org/ftp/python/3.11.6/python-3.11.6-embed-amd64.zip"

REM Extract Python
mkdir python_runtime
cd python_runtime
powershell -command "Expand-Archive ../python-embed.zip ."
cd ..

REM Download get-pip.py
curl -o get-pip.py "https://bootstrap.pypa.io/get-pip.py"

REM Install pip in embedded Python
python_runtime\python.exe get-pip.py

REM Install dependencies
python_runtime\python.exe -m pip install streamlit opencv-python pillow numpy scipy scikit-learn matplotlib

REM Create launcher
cat > start_checkresizer.bat << INNER_EOF
@echo off
cd /d "%~dp0"
echo Starting Check Resizer...
start "" "http://localhost:8501"
python_runtime\python.exe -m streamlit run ui.py --server.port 8501
pause
INNER_EOF

echo Portable Windows bundle created!
EOF

# Copy application files
echo "📋 Copying application files..."
cp ../ui.py ../check_resizer.py ../demo.py ../config.ini .

# Create universal README
cat > README_PORTABLE.txt << 'EOF'
# Check Resizer - Truly Portable Bundle

## 🎯 For Machines WITHOUT Python or Internet

This approach creates completely self-contained packages.

### Windows (Recommended)
1. Run: create_windows_portable.bat (on machine with internet)
2. Copy entire folder to target machine
3. Run: start_checkresizer.bat
4. No Python installation required!

### macOS
1. Option A: Use conda-pack (run create_conda_portable.sh)
2. Option B: Use the PyInstaller executable we built earlier
3. Copy to target machine and run

### Linux  
1. Use AppImage approach (run create_appimage.sh)
2. Creates single portable file
3. Copy and run on any Linux machine

## 📊 Size Comparison:
- Web app: ~20MB + Python (~50MB)
- Portable Python: ~150-300MB (includes everything)
- PyInstaller exe: ~170MB (single file)

## 🎯 Best Choice Per Scenario:

**Target has Python**: Use web app package
**Target has no Python, has internet**: Install Python + web app
**Target has no Python, no internet**: Use portable Python bundle
**Maximum compatibility**: Use PyInstaller executable (if working)
EOF

echo ""
echo "✅ Portable Python bundle framework created!"
echo "📁 Location: CheckResizer_Portable_Python/"
echo ""
echo "📋 Next steps for different platforms:"
echo "  Windows: Run create_windows_portable.bat"
echo "  macOS:   Run create_conda_portable.sh" 
echo "  Linux:   Run create_appimage.sh"