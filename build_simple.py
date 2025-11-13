#!/usr/bin/env python3
"""
Simple build script for Check Resizer executable
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def build_executable():
    """Build the standalone executable using PyInstaller."""
    print("🔨 Building Check Resizer executable...")
    print("=" * 50)
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    print("🧹 Cleaned previous builds")
    
    # Build using direct PyInstaller command with better options
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name=CheckResizer", 
        "--clean",
        "--collect-all=streamlit",
        "--collect-all=cv2",
        "--collect-all=PIL",
        "--collect-all=numpy",
        "--collect-all=scipy",
        "--collect-all=sklearn",
        "--hidden-import=streamlit.web.cli",
        "--hidden-import=streamlit.runtime.scriptrunner.magic_funcs",
        "--hidden-import=streamlit.components.v1",
        "--hidden-import=cv2",
        "--hidden-import=PIL.Image",
        "--hidden-import=numpy",
        "--hidden-import=scipy.ndimage",
        "--hidden-import=sklearn.cluster",
        "--add-data=ui.py:.",
        "--add-data=check_resizer.py:.",
        "--add-data=demo.py:.",
        "--add-data=config.ini:.",
        "--add-data=requirements.txt:.",
        "launch_simple.py"
    ]
    
    try:
        print("📦 Running PyInstaller with full collection...")
        print(f"Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable built successfully!")
            
            # Check if executable exists
            exe_path = Path("dist/CheckResizer")
            if sys.platform == "win32":
                exe_path = Path("dist/CheckResizer.exe")
                
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📁 Executable location: {exe_path}")
                print(f"📊 File size: {size_mb:.1f} MB")
                
                # Make executable on Unix systems
                if sys.platform != "win32":
                    os.chmod(exe_path, 0o755)
                
                create_distribution_package()
                return True
            else:
                print("❌ Executable file not found after build")
                return False
        else:
            print("❌ Build failed!")
            print("Error output:")
            print(result.stderr)
            print("\\nStdout output:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_distribution_package():
    """Create a distribution package."""
    print("\n📦 Creating distribution package...")
    
    dist_dir = Path("CheckResizer_Standalone")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copy executable
    if sys.platform == "win32":
        shutil.copy2("dist/CheckResizer.exe", dist_dir)
        exe_name = "CheckResizer.exe"
    else:
        shutil.copy2("dist/CheckResizer", dist_dir)
        exe_name = "CheckResizer"
    
    # Create README for users
    readme_content = f"""# Check Resizer Tool - Standalone

## Quick Start
1. Double-click `{exe_name}` to start the application
2. Wait for your web browser to open automatically
3. If browser doesn't open, go to: http://localhost:8501
4. Upload check images and download cropped results!

## Features
- Automatic whitespace removal from check images
- Multiple detection algorithms for best results
- 20-80% file size reduction
- Background leveling for scanned documents
- Manual cropping fallback option

## System Requirements
- No Python installation required
- Works on {sys.platform}
- Minimum 4GB RAM recommended
- Internet connection NOT required

## Troubleshooting
- If the browser doesn't open automatically, manually navigate to http://localhost:8501
- The application may take 10-30 seconds to start on first run
- Antivirus software may flag the executable (it's safe - add to whitelist if needed)
- For support, contact your system administrator

## Version Information
- Check Resizer Tool v1.0
- Built with PyInstaller
- Standalone executable (no dependencies)
"""
    
    (dist_dir / "README.txt").write_text(readme_content)
    
    # Create sample usage guide
    usage_guide = """# Usage Guide

## Step-by-Step Instructions

1. **Start the Application**
   - Double-click CheckResizer{'.exe' if sys.platform == 'win32' else ''}
   - A terminal window will open (do not close it)
   - Wait for "Starting Check Resizer Web UI..." message

2. **Access the Web Interface**
   - Your browser should open automatically to http://localhost:8501
   - If not, open any web browser and go to that address

3. **Upload Images**
   - Click "Browse files" or drag & drop check images
   - Supported formats: JPG, PNG, BMP, TIFF
   - Multiple files can be processed

4. **Process Images**
   - The tool automatically detects the best crop boundaries
   - Review the before/after comparison
   - Adjust settings in the sidebar if needed

5. **Download Results**
   - Click "Download Cropped Image" for each processed file
   - Files are saved with "_cropped" suffix

## Tips for Best Results
- Ensure good lighting when scanning/photographing checks
- Keep checks flat and straight
- Include some whitespace around the check edges
- Use high resolution (300+ DPI) for scanned images

## Advanced Settings
- **Background Leveling**: Enable for scanned documents with uneven lighting
- **Intensity**: Choose gentle/medium/strong based on image quality
- **Manual Cropping**: Available if automatic detection fails
"""
    
    (dist_dir / "Usage_Guide.txt").write_text(usage_guide)
    
    print(f"✅ Distribution package created: {dist_dir}")
    print(f"📁 Contents: executable, README, and usage guide")

def main():
    print("🚀 Check Resizer - Executable Builder")
    print("=" * 50)
    
    if build_executable():
        print("\n🎉 Build Complete!")
        print("=" * 50)
        print("📁 Standalone executable ready in: CheckResizer_Standalone/")
        print("\n💡 To deploy:")
        print("1. Copy the CheckResizer_Standalone folder to target machine")
        print("2. Run the executable - no Python installation needed!")
        print("3. Application will open in web browser automatically")
        
        print("\n📊 What's included:")
        print("- ✅ Standalone executable (no dependencies)")
        print("- ✅ README with instructions")
        print("- ✅ Usage guide")
        print("- ✅ All processing algorithms")
        print("- ✅ Web interface")
        
    else:
        print("\n❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()