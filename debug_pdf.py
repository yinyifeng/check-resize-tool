#!/usr/bin/env python3

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import os
import tempfile
from check_batch_processor import CheckBatchProcessor

def debug_pdf_generation():
    """Debug the PDF generation process step by step."""
    
    print("🔍 Debugging PDF Generation Process")
    print("=" * 50)
    
    # Create a simple test image that's clearly vertical
    print("\n📋 Creating test check image...")
    
    # Create a vertical check image (portrait orientation)
    height, width = 800, 400  # Clearly vertical
    test_image = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background
    
    # Add some check-like content
    cv2.rectangle(test_image, (20, 20), (width-20, height-20), (0, 0, 0), 2)
    cv2.putText(test_image, "TEST CHECK", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(test_image, "PAY TO:", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(test_image, "AMOUNT: $123.45", (30, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    # Add date line
    cv2.line(test_image, (200, 60), (350, 60), (0, 0, 0), 1)
    
    # Save test image
    test_path = "debug_test_check.png"
    cv2.imwrite(test_path, test_image)
    print(f"   Created test image: {test_path} ({width}x{height} - vertical)")
    
    # Test the resizer directly
    print("\n🔄 Testing CheckResizer...")
    from check_resizer import CheckResizer
    resizer = CheckResizer()
    
    # Test rotation detection
    print("   Testing rotation detection...")
    detected_rotation = resizer.detect_orientation(test_image)
    print(f"   Detected rotation needed: {detected_rotation}°")
    
    # Apply rotation
    rotated_image, applied_rotation = resizer.rotate_image_if_needed(test_image, auto_rotate=True)
    print(f"   Applied rotation: {applied_rotation}°")
    print(f"   Original dimensions: {width}x{height}")
    print(f"   Rotated dimensions: {rotated_image.shape[1]}x{rotated_image.shape[0]}")
    
    # Save rotated image
    rotated_path = "debug_rotated_check.png"
    cv2.imwrite(rotated_path, rotated_image)
    
    # Test full resize process
    print("\n📏 Testing full resize process...")
    output_path = "debug_processed_check.png"
    success = resizer.resize_image(test_path, output_path, auto_rotate=True, level_background=True)
    
    if success:
        processed_img = cv2.imread(output_path)
        print(f"   Processed successfully: {processed_img.shape[1]}x{processed_img.shape[0]}")
    else:
        print("   Processing failed!")
        return
    
    # Test classification
    print("\n📊 Testing check classification...")
    from check_batch_processor import CheckClassifier
    classifier = CheckClassifier()
    
    classification = classifier.classify_check(processed_img, "debug_test_check.png")
    print(f"   Type: {classification['type']}")
    print(f"   Confidence: {classification['confidence']:.1%}")
    print(f"   Dimensions: {classification['dimensions']['width_inches']:.2f}\" x {classification['dimensions']['height_inches']:.2f}\"")
    print(f"   Aspect ratio: {classification['dimensions']['aspect_ratio']:.2f}")
    print(f"   Estimated DPI: {classification['dimensions']['estimated_dpi']}")
    
    # Test PDF generation with single check
    print("\n📄 Testing PDF generation...")
    processor = CheckBatchProcessor()
    
    # Create check info structure
    check_info = {
        'original_path': test_path,
        'processed_path': output_path,
        'classification': classification
    }
    
    # Create PDF with single check
    output_dir = "./debug_pdf_output"
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_path = processor._create_print_pdf([check_info], classification['type'], output_dir)
    print(f"   Generated PDF: {pdf_path}")
    
    # Show dimensions used in PDF
    from check_batch_processor import CheckClassifier
    check_specs = CheckClassifier.CHECK_TYPES[classification['type']]
    print(f"   Target check dimensions: {check_specs['width']}\" x {check_specs['height']}\"")
    print(f"   Target aspect ratio: {check_specs['aspect_ratio']:.2f}")
    
    # Clean up
    print("\n🧹 Cleaning up...")
    for file in [test_path, rotated_path, output_path]:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Removed: {file}")
    
    print(f"\n✅ Debug complete! Check the PDF: {pdf_path}")
    print(f"📁 Output directory: {output_dir}")

if __name__ == "__main__":
    debug_pdf_generation()