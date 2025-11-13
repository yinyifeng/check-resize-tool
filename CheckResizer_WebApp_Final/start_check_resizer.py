#!/usr/bin/env python3
"""
Simple launcher for Check Resizer Web Application
"""
import subprocess
import sys
import webbrowser
import time
import threading
import os

def open_browser():
    """Open browser after server starts."""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:8501')
        print("🌐 Browser opened to http://localhost:8501")
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")
        print("   Please manually open: http://localhost:8501")

def main():
    """Launch Check Resizer web application."""
    print("🚀 Starting Check Resizer Web Application...")
    print("=" * 50)
    print("📁 Working directory:", os.getcwd())
    print("🐍 Python executable:", sys.executable)
    print("🌐 Starting web server...")
    print()
    print("💡 Browser will open automatically to http://localhost:8501")
    print("💡 To stop the server, press Ctrl+C")
    print("=" * 50)
    
    try:
        # Start browser opener in background
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run Streamlit directly
        cmd = [
            sys.executable, "-m", "streamlit", "run", "ui.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Check Resizer...")
    except FileNotFoundError:
        print("❌ Error: ui.py not found in current directory")
        print("   Make sure you're running from the CheckResizer directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Check that all required packages are installed:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()