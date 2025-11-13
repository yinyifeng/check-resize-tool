#!/usr/bin/env python3
"""
Quick launcher for the Check Resizer Web UI
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit UI."""
    
    print("🚀 Starting Check Resizer Web UI...")
    print("=" * 40)
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    ui_script = script_dir / "ui.py"
    
    # Check if virtual environment is activated
    venv_python = script_dir / ".venv" / "bin" / "python"
    
    if venv_python.exists():
        python_cmd = str(venv_python)
        print("✅ Using virtual environment")
    else:
        python_cmd = sys.executable
        print("⚠️  Using system Python (virtual environment not found)")
    
    # Check if ui.py exists
    if not ui_script.exists():
        print(f"❌ UI script not found: {ui_script}")
        sys.exit(1)
    
    print(f"📁 Working directory: {script_dir}")
    print(f"🐍 Python executable: {python_cmd}")
    print(f"🌐 Starting web interface...")
    print()
    print("💡 The web interface will open in your default browser")
    print("💡 To stop the server, press Ctrl+C in this terminal")
    print("=" * 40)
    
    try:
        # Change to the script directory
        os.chdir(script_dir)
        
        # Launch streamlit
        cmd = [python_cmd, "-m", "streamlit", "run", "ui.py"]
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Check Resizer Web UI...")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()