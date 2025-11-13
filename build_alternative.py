#!/usr/bin/env python3
"""
Alternative build script that ensures all dependencies are properly installed
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def install_build_dependencies():
    """Install additional packages that PyInstaller might need."""
    print("📦 Installing build dependencies...")
    
    # Packages that help with PyInstaller
    build_deps = [
        "pyinstaller[hooks]",
        "altair",  # Streamlit dependency
        "plotly",  # Streamlit dependency  
        "pyarrow", # Data handling
        "watchdog", # File watching
        "click",   # CLI tools
        "tornado", # Web server
        "packaging", # Package metadata
        "importlib-metadata", # Package discovery
    ]
    
    for dep in build_deps:
        try:
            print(f"  Installing {dep}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Could not install {dep}: {e}")
    
    print("✅ Dependencies installation completed")

def build_with_alternative_method():
    """Try building with a more comprehensive approach."""
    print("🔨 Building with alternative method...")
    
    # Clean up
    for dir_name in ["build", "dist", "__pycache__"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Build command with extensive options
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name=CheckResizer",
        "--clean", 
        "--noconfirm",
        # Collect everything for major packages
        "--collect-all=streamlit",
        "--collect-all=altair", 
        "--collect-all=plotly",
        "--collect-all=click",
        "--collect-all=tornado",
        # Hidden imports
        "--hidden-import=streamlit",
        "--hidden-import=streamlit.web.cli",
        "--hidden-import=streamlit.web.bootstrap",
        "--hidden-import=streamlit.runtime",
        "--hidden-import=streamlit.runtime.scriptrunner",
        "--hidden-import=streamlit.runtime.scriptrunner.magic_funcs",
        "--hidden-import=streamlit.components.v1",
        "--hidden-import=streamlit.delta_generator",
        "--hidden-import=altair",
        "--hidden-import=plotly",
        "--hidden-import=plotly.graph_objects",
        "--hidden-import=click",
        "--hidden-import=tornado",
        "--hidden-import=tornado.web",
        "--hidden-import=cv2",
        "--hidden-import=PIL.Image",
        "--hidden-import=numpy",
        "--hidden-import=scipy.ndimage",
        "--hidden-import=sklearn.cluster",
        "--hidden-import=matplotlib.pyplot",
        # Data files
        "--add-data=ui.py:.",
        "--add-data=check_resizer.py:.",
        "--add-data=demo.py:.", 
        "--add-data=config.ini:.",
        "--add-data=requirements.txt:.",
        # Source file
        "launch_simple.py"
    ]
    
    print("📦 Running comprehensive PyInstaller build...")
    print(f"Command: {' '.join(cmd[:10])}... (truncated)")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            return True
        else:
            print("❌ Build failed!")
            print("STDERR:")
            print(result.stderr)
            print("\nSTDOUT:")
            print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build timed out (10 minutes)")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_simple_launcher():
    """Create a simpler launcher script."""
    launcher_content = '''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the bundle directory to Python path
if getattr(sys, 'frozen', False):
    bundle_dir = Path(sys._MEIPASS)
    sys.path.insert(0, str(bundle_dir))
    os.chdir(bundle_dir)

# Import and run
try:
    import streamlit.web.cli as stcli
    sys.argv = ["streamlit", "run", "ui.py", "--server.port=8501"]
    stcli.main()
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to exit...")
'''
    
    with open("launch_minimal.py", "w") as f:
        f.write(launcher_content)
    
    return "launch_minimal.py"

def main():
    print("🚀 Check Resizer - Alternative Build Method")
    print("=" * 60)
    
    # Step 1: Install dependencies
    install_build_dependencies()
    
    # Step 2: Create minimal launcher
    launcher = create_simple_launcher()
    print(f"✅ Created launcher: {launcher}")
    
    # Step 3: Try to build
    if build_with_alternative_method():
        print("\n🎉 Build successful!")
        
        # Check result
        exe_path = Path("dist/CheckResizer")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024) 
            print(f"📁 Executable: {exe_path}")
            print(f"📊 Size: {size_mb:.1f} MB")
            
            # Make executable
            os.chmod(exe_path, 0o755)
            
            print("\n✅ Ready for testing!")
            print("Try running: ./dist/CheckResizer")
        else:
            print("❌ Executable not found")
    else:
        print("\n❌ Build failed with alternative method")
        print("You may need to:")
        print("1. Update PyInstaller: pip install --upgrade pyinstaller")
        print("2. Install missing packages manually")
        print("3. Check Python version compatibility")

if __name__ == "__main__":
    main()