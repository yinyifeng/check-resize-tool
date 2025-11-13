#!/usr/bin/env python3
"""
Test script to verify the check resizer tool installation and functionality.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing package imports...")
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✓ Matplotlib imported successfully")
    except ImportError as e:
        print(f"✗ Matplotlib import failed: {e}")
        return False
    
    return True

def test_check_resizer():
    """Test if the CheckResizer class can be imported and initialized."""
    print("\nTesting CheckResizer class...")
    
    try:
        from check_resizer import CheckResizer
        resizer = CheckResizer()
        print("✓ CheckResizer class imported and initialized successfully")
        print(f"✓ Supported formats: {resizer.supported_formats}")
        return True
    except ImportError as e:
        print(f"✗ CheckResizer import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ CheckResizer initialization failed: {e}")
        return False

def create_test_image():
    """Create a simple test image for processing."""
    print("\nCreating test image...")
    
    try:
        from PIL import Image, ImageDraw
        import numpy as np
        
        # Create a white image with a black rectangle (simulating a check)
        width, height = 800, 600
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Draw a black rectangle (simulating check content)
        margin = 100
        draw.rectangle([margin, margin, width-margin, height-margin], 
                      outline='black', width=3)
        
        # Add some text
        draw.text((margin+20, margin+20), "Sample Check", fill='black')
        draw.text((margin+20, height-margin-40), "Test Image", fill='black')
        
        # Save test image
        test_image_path = "test_check.png"
        image.save(test_image_path)
        print(f"✓ Test image created: {test_image_path}")
        
        return test_image_path
    except Exception as e:
        print(f"✗ Failed to create test image: {e}")
        return None

def test_processing(test_image_path):
    """Test the actual image processing functionality."""
    print(f"\nTesting image processing with {test_image_path}...")
    
    try:
        from check_resizer import CheckResizer
        
        resizer = CheckResizer()
        
        # Test loading
        cv_image, pil_image = resizer.load_image(test_image_path)
        if cv_image is None:
            print("✗ Failed to load test image")
            return False
        
        print("✓ Image loaded successfully")
        
        # Test analysis
        bounds = resizer.analyze_image(cv_image)
        if bounds is None:
            print("✗ Failed to analyze image")
            return False
        
        print(f"✓ Image analysis successful, bounds: {bounds}")
        
        # Test actual processing
        output_path = "test_check_resized.png"
        success = resizer.resize_image(test_image_path, output_path)
        
        if success and os.path.exists(output_path):
            print(f"✓ Image processing successful, output saved to: {output_path}")
            
            # Clean up
            os.remove(output_path)
            print("✓ Cleanup completed")
            return True
        else:
            print("✗ Image processing failed")
            return False
            
    except Exception as e:
        print(f"✗ Processing test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Check Resizer Tool - Installation Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please install required packages:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Test CheckResizer class
    if not test_check_resizer():
        print("\n❌ CheckResizer class test failed.")
        sys.exit(1)
    
    # Create and test with a sample image
    test_image = create_test_image()
    if test_image is None:
        print("\n❌ Could not create test image.")
        sys.exit(1)
    
    # Test processing
    if not test_processing(test_image):
        print("\n❌ Image processing test failed.")
        # Clean up test image
        if os.path.exists(test_image):
            os.remove(test_image)
        sys.exit(1)
    
    # Clean up test image
    if os.path.exists(test_image):
        os.remove(test_image)
        print("✓ Test image cleaned up")
    
    print("\n🎉 All tests passed! The check resizer tool is ready to use.")
    print("\nUsage examples:")
    print("  python check_resizer.py your_check.jpg")
    print("  python check_resizer.py your_check.jpg --preview")
    print("  python check_resizer.py check_folder/ --batch")

if __name__ == "__main__":
    main()