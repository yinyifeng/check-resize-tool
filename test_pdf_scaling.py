#!/usr/bin/env python3

import cv2
import numpy as np
from PIL import Image
import os
from check_batch_processor import CheckBatchProcessor

def create_test_check_with_ruler():
    """Create a test check with ruler markings to verify scaling."""
    
    # Create personal check at 300 DPI (6" x 2.75" = 1800 x 825 pixels)
    width_pixels = int(6 * 300)  # 1800
    height_pixels = int(2.75 * 300)  # 825
    
    print(f"Creating test check: {width_pixels}x{height_pixels} pixels (6\" x 2.75\" at 300 DPI)")
    
    # Create white background
    image = np.ones((height_pixels, width_pixels, 3), dtype=np.uint8) * 255
    
    # Add border
    cv2.rectangle(image, (20, 20), (width_pixels-20, height_pixels-20), (0, 0, 0), 3)
    
    # Add ruler markings along top (inches)
    for inch in range(1, 6):
        x = inch * 300  # 300 pixels per inch
        cv2.line(image, (x, 20), (x, 60), (255, 0, 0), 2)
        cv2.putText(image, f"{inch}\"", (x-15, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    # Add ruler markings along left side (inches)  
    for inch in range(1, 3):
        y = inch * 300  # 300 pixels per inch
        if y < height_pixels - 20:
            cv2.line(image, (20, y), (80, y), (255, 0, 0), 2)
            cv2.putText(image, f"{inch}\"", (85, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    # Add check content
    cv2.putText(image, "SCALE TEST CHECK", (100, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    cv2.putText(image, "This check should be exactly 6\" x 2.75\" in the PDF", (100, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(image, "PAY TO THE ORDER OF", (100, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.line(image, (300, 220), (width_pixels-100, 220), (0, 0, 0), 2)
    
    cv2.putText(image, "$", (100, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.line(image, (130, 280), (width_pixels-100, 280), (0, 0, 0), 2)
    
    # Add measurements text
    cv2.putText(image, f"Target: 6.00\" x 2.75\"", (100, height_pixels-80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 100, 0), 2)
    cv2.putText(image, f"Pixels: {width_pixels} x {height_pixels}", (100, height_pixels-50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 100, 0), 2)
    
    return image

def test_pdf_scaling():
    """Test PDF scaling with ruler measurements."""
    
    print("📏 Testing PDF Scaling with Ruler Measurements")
    print("=" * 55)
    
    # Create test check with ruler
    test_image = create_test_check_with_ruler()
    
    # Save test check in different orientations
    test_dir = "./scale_test_output"
    os.makedirs(test_dir, exist_ok=True)
    
    test_files = []
    
    # Horizontal orientation (correct)
    horizontal_path = os.path.join(test_dir, "scale_test_horizontal.png") 
    cv2.imwrite(horizontal_path, test_image)
    test_files.append(horizontal_path)
    print(f"✅ Saved horizontal: {test_image.shape[1]}x{test_image.shape[0]}")
    
    # Vertical orientation (needs rotation)
    vertical_image = cv2.rotate(test_image, cv2.ROTATE_90_CLOCKWISE)
    vertical_path = os.path.join(test_dir, "scale_test_vertical.png")
    cv2.imwrite(vertical_path, vertical_image) 
    test_files.append(vertical_path)
    print(f"✅ Saved vertical: {vertical_image.shape[1]}x{vertical_image.shape[0]}")
    
    # Process with batch processor
    print(f"\n🔄 Processing scale test checks...")
    processor = CheckBatchProcessor()
    processor.auto_rotate = True
    processor.level_background = False  # Don't modify for scale test
    
    results = processor.process_batch(test_files, test_dir)
    
    # Show results
    print(f"\n📊 Scale Test Results:")
    for i, check_info in enumerate(results['processed_checks']):
        classification = check_info['classification']
        original_name = os.path.basename(check_info['original_path'])
        print(f"   {i+1}. {original_name}")
        print(f"      Type: {classification['type']} ({classification['confidence']:.1%})")
        print(f"      Measured: {classification['dimensions']['width_inches']:.2f}\" x {classification['dimensions']['height_inches']:.2f}\"")
        print(f"      Expected: 6.00\" x 2.75\"")
        print(f"      Scale accuracy: {abs(classification['dimensions']['width_inches'] - 6.0)/6.0*100:.1f}% width error, {abs(classification['dimensions']['height_inches'] - 2.75)/2.75*100:.1f}% height error")
    
    # Show PDF info
    print(f"\n📄 Generated PDF:")
    for pdf_info in results['pdf_files']:
        file_size = os.path.getsize(pdf_info['path']) / 1024
        print(f"   {pdf_info['type'].title()}: {os.path.basename(pdf_info['path'])} ({file_size:.1f} KB)")
        print(f"   📏 This PDF should show checks at exactly 6\" x 2.75\" when printed")
        
    print(f"\n🎯 Scale Verification Instructions:")
    print(f"   1. Open the generated PDF")
    print(f"   2. Print at 100% scale (no scaling)")  
    print(f"   3. Measure the printed checks with a ruler")
    print(f"   4. They should be exactly 6\" wide x 2.75\" tall")
    print(f"   5. The ruler markings in the image should align with actual measurements")
    
    print(f"\n✅ Scale test complete!")
    print(f"📁 Files saved to: {test_dir}")

if __name__ == "__main__":
    test_pdf_scaling()