#!/usr/bin/env python3
"""
Simple file server for downloading batch processing results
Use this if Streamlit downloads are not working properly
"""

import os
import http.server
import socketserver
import webbrowser
from pathlib import Path
import argparse

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add headers to force download for PDF files
        if self.path.endswith('.pdf'):
            self.send_header('Content-Type', 'application/pdf')
            filename = Path(self.path).name
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        elif self.path.endswith('.zip'):
            self.send_header('Content-Type', 'application/zip')
            filename = Path(self.path).name
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        super().end_headers()

def start_file_server(directory=".", port=8503):
    """Start a simple file server for downloading files."""
    
    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        return False
    
    # Change to the target directory
    os.chdir(directory)
    
    # List available files
    pdf_files = list(Path(".").glob("*.pdf"))
    zip_files = list(Path(".").glob("*.zip"))
    txt_files = list(Path(".").glob("*.txt"))
    json_files = list(Path(".").glob("*.json"))
    
    print(f"📁 Serving files from: {os.getcwd()}")
    print(f"📄 Available PDFs: {len(pdf_files)}")
    for pdf in pdf_files:
        size = os.path.getsize(pdf) / 1024
        print(f"   • {pdf.name} ({size:.1f} KB)")
    
    if zip_files:
        print(f"📦 Available ZIPs: {len(zip_files)}")
        for zip_file in zip_files:
            size = os.path.getsize(zip_file) / 1024
            print(f"   • {zip_file.name} ({size:.1f} KB)")
    
    if txt_files or json_files:
        print(f"📝 Summary files: {len(txt_files + json_files)}")
        for file in txt_files + json_files:
            print(f"   • {file.name}")
    
    # Start the server
    try:
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            print(f"\n🌐 File server running at: http://localhost:{port}")
            print(f"🔗 Click on files to download them")
            print(f"🛑 Press Ctrl+C to stop the server")
            print("=" * 50)
            
            # Try to open browser
            try:
                webbrowser.open(f"http://localhost:{port}")
            except:
                pass
            
            httpd.serve_forever()
    
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped.")
        return True
    
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Try a different port:")
            print(f"   python download_server.py --port {port + 1}")
        else:
            print(f"❌ Error starting server: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Simple file server for batch processing downloads")
    parser.add_argument(
        "--directory", "-d", 
        default="./demo_batch_output",
        help="Directory to serve files from (default: ./demo_batch_output)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8503,
        help="Port to run the server on (default: 8503)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Batch Processing File Server")
    print("=" * 40)
    print("This server provides an alternative way to download")
    print("batch processing results if Streamlit downloads fail.")
    print()
    
    # Check common output directories
    possible_dirs = [
        args.directory,
        "./test_batch_output",
        "./demo_batch_output",
        "."
    ]
    
    target_dir = None
    for check_dir in possible_dirs:
        if os.path.exists(check_dir):
            pdf_count = len(list(Path(check_dir).glob("*.pdf")))
            if pdf_count > 0:
                target_dir = check_dir
                print(f"✅ Found {pdf_count} PDFs in: {check_dir}")
                break
    
    if not target_dir:
        print("⚠️  No PDF files found in common directories.")
        print("   Make sure you have run batch processing first:")
        print("   python demo_batch.py")
        print("   python start_batch_processor.py")
        print()
        target_dir = args.directory  # Use specified directory anyway
    
    success = start_file_server(target_dir, args.port)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())