#!/usr/bin/env python3
"""
Executable launcher for the Check Resizer Web UI
This version works when bundled with PyInstaller
"""

import subprocess
import sys
import os
from pathlib import Path
import tempfile
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

def main():
    """Launch the Streamlit UI from bundled executable."""
    
    # Prevent recursive launching if we're already running as part of Streamlit
    if 'streamlit' in sys.modules or 'STREAMLIT_SERVER_PORT' in os.environ:
        print("⚠️  Already running within Streamlit - preventing recursive launch")
        return
    
    print("🚀 Starting Check Resizer Web UI...")
    print("=" * 40)
    
    # Get bundled directory
    bundle_dir = get_bundled_dir()
    ui_script = bundle_dir / "ui.py"
    
    print(f"📁 Bundle directory: {bundle_dir}")
    print(f"🐍 Python executable: {sys.executable}")
    print(f"🌐 Starting web interface...")
    print()
    print("💡 The web interface will open automatically")
    print("💡 To stop the server, close this window or press Ctrl+C")
    print("=" * 40)
    
    # Check if ui.py exists in bundle
    if not ui_script.exists():
        print(f"❌ UI script not found in bundle: {ui_script}")
        
        # Try to find it in the same directory as the executable
        exe_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
        ui_script = exe_dir / "ui.py"
        
        if ui_script.exists():
            print(f"✅ Found UI script: {ui_script}")
            bundle_dir = exe_dir
        else:
            print("❌ Could not find ui.py")
            print("Available files in bundle:")
            try:
                for f in bundle_dir.iterdir():
                    print(f"  - {f.name}")
            except:
                pass
            input("Press Enter to exit...")
            sys.exit(1)
    
    try:
        # Change to bundle directory
        original_cwd = os.getcwd()
        os.chdir(bundle_dir)
        
        def open_browser():
            """Open browser after a delay."""
            time.sleep(3)  # Wait for Streamlit to start
            try:
                webbrowser.open('http://localhost:8501')
            except:
                pass  # Ignore browser errors
        
        # Start browser opener in background
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Check if port is already in use
        import socket
        def is_port_in_use(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', port))
                    return False
                except OSError:
                    return True
        
        if is_port_in_use(8501):
            print("⚠️  Port 8501 is already in use!")
            print("   Another instance may be running.")
            print("   Try opening: http://localhost:8501")
            input("Press Enter to exit...")
            sys.exit(0)
        
        # Launch streamlit with better error handling
        cmd = [
            sys.executable, "-m", "streamlit", "run", str(ui_script),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--server.enableXsrfProtection", "false"
        ]
        
        print("🚀 Launching Streamlit server...")
        print(f"Command: {' '.join(cmd)}")
        
        # Use subprocess.Popen for better control
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Monitor the process
        try:
            # Wait a bit to see if it starts successfully
            import time
            time.sleep(2)
            
            if process.poll() is None:
                print("✅ Server started successfully!")
                print("🌐 Opening browser to http://localhost:8501")
                
                # Wait for the process to complete
                process.wait()
            else:
                print("❌ Server failed to start")
                print("Error output:")
                output = process.stdout.read()
                print(output)
        except KeyboardInterrupt:
            print("\n👋 Shutting down server...")
            process.terminate()
            process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Check Resizer Web UI...")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        print(f"Error details: {type(e).__name__}: {str(e)}")
        input("Press Enter to exit...")
        sys.exit(1)
    finally:
        # Restore original working directory
        try:
            os.chdir(original_cwd)
        except:
            pass

if __name__ == "__main__":
    main()