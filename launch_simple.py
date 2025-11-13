#!/usr/bin/env python3
"""
Simple launcher that directly runs the UI without subprocess calls
This prevents the infinite loop issue
"""

import sys
import os
from pathlib import Path
import webbrowser
import time
import threading

def get_bundled_dir():
    """Get the directory containing bundled files."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running as script
        return Path(__file__).parent

def open_browser_delayed():
    """Open browser after a delay."""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:8501')
        print("🌐 Browser should now open to http://localhost:8501")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Please manually open: http://localhost:8501")

def main():
    """Launch the UI directly using Streamlit's main function."""
    
    print("🚀 Starting Check Resizer Web UI...")
    print("=" * 40)
    
    # Get bundled directory and change to it
    bundle_dir = get_bundled_dir()
    original_cwd = os.getcwd()
    
    try:
        os.chdir(bundle_dir)
        print(f"📁 Working directory: {bundle_dir}")
        
        # Import Streamlit and run directly
        import streamlit.web.cli as stcli
        
        # Start browser opener in background
        browser_thread = threading.Thread(target=open_browser_delayed)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("🚀 Starting web interface...")
        print("💡 Browser will open automatically")
        print("💡 To stop, close this window or press Ctrl+C")
        print("=" * 40)
        
        # Set up Streamlit arguments properly
        sys.argv = [
            "streamlit",
            "run", 
            "ui.py",
            "--server.port=8501",
            "--server.address=localhost", 
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.enableXsrfProtection=false",
            "--global.developmentMode=false"
        ]
        
        # Run Streamlit directly
        stcli.main()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Check Resizer Web UI...")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Available files:")
        try:
            for f in sorted(bundle_dir.iterdir()):
                print(f"  - {f.name}")
        except:
            pass
        input("Press Enter to exit...")
    finally:
        try:
            os.chdir(original_cwd)
        except:
            pass

if __name__ == "__main__":
    main()