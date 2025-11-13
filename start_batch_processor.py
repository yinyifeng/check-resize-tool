#!/usr/bin/env python3
"""
Launcher for Check Batch Processor UI
Starts Streamlit application for batch processing checks
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the batch processing UI."""
    
    print("🚀 Starting Check Batch Processor UI...")
    print("=" * 50)
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    batch_ui_path = script_dir / "batch_ui.py"
    
    # Check if batch_ui.py exists
    if not batch_ui_path.exists():
        print(f"❌ Error: {batch_ui_path} not found!")
        return 1
    
    # Check if required dependencies are available
    try:
        import streamlit
        import reportlab
        import sklearn
        print("✅ Dependencies verified")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nPlease install required packages:")
        print("pip install streamlit reportlab scikit-learn")
        return 1
    
    # Launch Streamlit
    try:
        print(f"🌐 Launching Streamlit UI...")
        print(f"📂 App location: {batch_ui_path}")
        print("\n" + "=" * 50)
        print("🔗 Your app will open in your default web browser")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(batch_ui_path),
            "--server.port", "8502",  # Use different port than main UI
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())