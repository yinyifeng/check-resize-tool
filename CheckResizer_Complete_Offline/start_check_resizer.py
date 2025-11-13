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
