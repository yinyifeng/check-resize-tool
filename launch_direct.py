#!/usr/bin/env python3
"""
Direct UI runner that bypasses Streamlit CLI issues
"""

import sys
import os
from pathlib import Path
import webbrowser
import time
import threading

def main():
    """Run the UI directly without Streamlit CLI."""
    
    print("🚀 Check Resizer - Starting Web Interface...")
    print("=" * 50)
    
    # Get bundle directory
    if getattr(sys, 'frozen', False):
        bundle_dir = Path(sys._MEIPASS)
    else:
        bundle_dir = Path(__file__).parent
    
    # Change to bundle directory  
    original_cwd = os.getcwd()
    os.chdir(bundle_dir)
    
    print(f"📁 Working directory: {bundle_dir}")
    print("🌐 Initializing web server...")
    
    try:
        # Import UI module directly
        sys.path.insert(0, str(bundle_dir))
        
        # Set environment to avoid development mode issues
        os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
        os.environ["STREAMLIT_SERVER_PORT"] = "8501"
        os.environ["STREAMLIT_SERVER_ADDRESS"] = "localhost"
        os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
        os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        
        # Import and configure Streamlit
        import streamlit as st
        from streamlit.web import cli as stcli
        from streamlit import config
        
        # Set configuration programmatically
        config.set_option("server.port", 8501)
        config.set_option("server.address", "localhost")
        config.set_option("server.headless", True)
        config.set_option("browser.gatherUsageStats", False)
        config.set_option("global.developmentMode", False)
        config.set_option("server.enableXsrfProtection", False)
        
        def open_browser():
            time.sleep(3)
            try:
                webbrowser.open('http://localhost:8501')
                print("🌐 Browser opened to http://localhost:8501")
            except:
                print("⚠️  Please manually open: http://localhost:8501")
        
        # Start browser opener
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("✅ Configuration set")
        print("🚀 Starting Streamlit server...")
        print("💡 Browser will open automatically")
        print("💡 To stop, close this window or press Ctrl+C")
        print("=" * 50)
        
        # Run with modified argv
        sys.argv = ["streamlit", "run", "ui.py"]
        stcli.main()
        
    except KeyboardInterrupt:
        print("\\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        print("\\n📁 Available files in bundle:")
        try:
            for f in sorted(bundle_dir.iterdir())[:20]:  # Show first 20 files
                print(f"  - {f.name}")
            if len(list(bundle_dir.iterdir())) > 20:
                print("  ... and more")
        except:
            pass
            
        input("\\nPress Enter to exit...")
        
    finally:
        try:
            os.chdir(original_cwd)
        except:
            pass

if __name__ == "__main__":
    main()