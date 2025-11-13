#!/usr/bin/env python3
"""
Test script to verify PDF download functionality
Creates a simple batch and tests the complete workflow
"""

import os
import tempfile
import shutil
from pathlib import Path
from check_batch_processor import CheckBatchProcessor
from demo_batch import create_sample_check

def test_pdf_downloads():
    """Test the PDF download functionality."""
    
    print("🧪 Testing PDF Download Functionality")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a few sample checks
        sample_dir = os.path.join(temp_dir, "samples")
        os.makedirs(sample_dir, exist_ok=True)
        
        # Create one of each type for testing
        image_paths = []
        check_types = ['personal', 'business', 'commercial']
        
        for i, check_type in enumerate(check_types):
            filename = os.path.join(sample_dir, f"test_{check_type}.png")
            create_sample_check(check_type, filename, dpi=300)
            image_paths.append(filename)
            print(f"✅ Created test {check_type} check: {Path(filename).name}")
        
        # Process the batch
        print("\n🔄 Processing batch...")
        processor = CheckBatchProcessor()
        output_dir = os.path.join(temp_dir, "output")
        
        results = processor.process_batch(image_paths, output_dir)
        
        # Verify PDF files were created
        print(f"\n📊 Results:")
        print(f"  Processed: {len(results['processed_checks'])} checks")
        print(f"  PDF files: {len(results['pdf_files'])}")
        print(f"  Errors: {len(results['errors'])}")
        
        # Test PDF file access
        print(f"\n📄 Testing PDF files:")
        all_files_exist = True
        total_size = 0
        
        for pdf_info in results['pdf_files']:
            pdf_path = pdf_info['path']
            filename = Path(pdf_path).name
            
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                total_size += file_size
                print(f"  ✅ {filename}: {file_size / 1024:.1f} KB")
                
                # Test reading the file
                try:
                    with open(pdf_path, 'rb') as f:
                        data = f.read()
                    print(f"     📖 File readable: {len(data)} bytes")
                except Exception as e:
                    print(f"     ❌ Error reading file: {e}")
                    all_files_exist = False
            else:
                print(f"  ❌ Missing: {filename}")
                all_files_exist = False
        
        print(f"\n📈 Summary:")
        print(f"  Total PDF size: {total_size / 1024:.1f} KB")
        print(f"  All files accessible: {'✅ Yes' if all_files_exist else '❌ No'}")
        
        # Test ZIP creation
        print(f"\n📦 Testing ZIP creation...")
        try:
            from batch_ui import create_download_zip
            zip_path = create_download_zip(results, temp_dir)
            
            if zip_path and os.path.exists(zip_path):
                zip_size = os.path.getsize(zip_path)
                print(f"  ✅ ZIP created: {zip_size / 1024:.1f} KB")
                
                # Test reading ZIP
                with open(zip_path, 'rb') as f:
                    zip_data = f.read()
                print(f"  📖 ZIP readable: {len(zip_data)} bytes")
            else:
                print(f"  ❌ ZIP creation failed")
                
        except Exception as e:
            print(f"  ❌ ZIP error: {e}")
        
        # Copy files to permanent location for inspection
        permanent_dir = "./test_batch_output"
        if os.path.exists(permanent_dir):
            shutil.rmtree(permanent_dir)
        
        shutil.copytree(output_dir, permanent_dir)
        print(f"\n💾 Test files saved to: {permanent_dir}")
        
        return all_files_exist

if __name__ == "__main__":
    success = test_pdf_downloads()
    print(f"\n🎯 Test Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("\nPDF download functionality is working correctly!")
        print("You can now upload files to the web UI and download PDFs.")
    else:
        print("\nThere are issues with PDF file creation or access.")
        print("Check the error messages above for details.")