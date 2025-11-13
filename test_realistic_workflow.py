#!/usr/bin/env python3

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import os
import tempfile
from check_batch_processor import CheckBatchProcessor, CheckClassifier

def create_realistic_check(width, height, check_type, rotation=0):
    """Create a realistic check image with proper content."""
    
    # Create base image
    image = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background
    
    # Add check border
    cv2.rectangle(image, (10, 10), (width-10, height-10), (0, 0, 0), 2)
    
    # Add check content based on type
    if check_type == 'personal':
        # Personal check layout
        cv2.putText(image, "JOHN DOE", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        cv2.putText(image, "123 Main St", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        cv2.putText(image, "PAY TO THE ORDER OF", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        cv2.line(image, (180, 100), (width-30, 100), (0, 0, 0), 1)
        cv2.putText(image, "$ ", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.line(image, (40, 130), (width-30, 130), (0, 0, 0), 1)
        
    elif check_type == 'business':
        # Business check layout  
        cv2.putText(image, "ACME CORPORATION", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(image, "555 Business Blvd", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        cv2.putText(image, "PAY TO THE ORDER OF", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.line(image, (200, 110), (width-30, 110), (0, 0, 0), 1)
        cv2.putText(image, "$ ", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        cv2.line(image, (50, 140), (width-30, 140), (0, 0, 0), 1)
        
    elif check_type == 'commercial':
        # Commercial voucher-style check
        cv2.putText(image, "CORPORATE PAYMENT VOUCHER", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(image, "BigCorp Industries Inc.", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        cv2.putText(image, "VENDOR:", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.line(image, (90, 120), (width-30, 120), (0, 0, 0), 1)
        cv2.putText(image, "AMOUNT:", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.line(image, (100, 150), (width-30, 150), (0, 0, 0), 1)
        # Add more lines for commercial voucher
        for i, label in enumerate(["INVOICE #:", "DATE:", "APPROVED BY:"]):
            y_pos = 180 + (i * 30)
            if y_pos < height - 30:
                cv2.putText(image, label, (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                cv2.line(image, (120, y_pos), (width-30, y_pos), (0, 0, 0), 1)
    
    # Add check number
    cv2.putText(image, f"#{1000 + np.random.randint(0, 9999)}", (width-100, height-20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    
    # Apply rotation if specified
    if rotation == 90:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 180:
        image = cv2.rotate(image, cv2.ROTATE_180)
    elif rotation == 270:
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    return image

def test_complete_workflow():
    """Test the complete workflow with realistic checks."""
    
    print("🧪 Testing Complete Check Processing Workflow")
    print("=" * 55)
    
    # Create realistic test checks with different orientations
    test_checks = [
        # Personal checks
        ("personal_horizontal.png", create_realistic_check(600*2, 275*2, 'personal', 0)),
        ("personal_vertical.png", create_realistic_check(275*2, 600*2, 'personal', 90)),
        
        # Business checks  
        ("business_horizontal.png", create_realistic_check(850*2, 350*2, 'business', 0)),
        ("business_rotated.png", create_realistic_check(350*2, 850*2, 'business', 270)),
        
        # Commercial checks
        ("commercial_horizontal.png", create_realistic_check(850*2, 1100*2, 'commercial', 0)),
        ("commercial_vertical.png", create_realistic_check(1100*2, 850*2, 'commercial', 90)),
    ]
    
    # Create test directory
    test_dir = "./test_realistic_checks"
    os.makedirs(test_dir, exist_ok=True)
    
    # Save test images
    test_paths = []
    print("\n📋 Creating realistic test check images...")
    for filename, image in test_checks:
        filepath = os.path.join(test_dir, filename)
        cv2.imwrite(filepath, image)
        test_paths.append(filepath)
        print(f"   ✅ {filename}: {image.shape[1]}x{image.shape[0]}")
    
    # Process with batch processor
    print(f"\n🔄 Processing {len(test_paths)} realistic checks...")
    processor = CheckBatchProcessor()
    processor.auto_rotate = True
    processor.level_background = True
    
    output_dir = "./test_realistic_output"
    results = processor.process_batch(test_paths, output_dir)
    
    # Show results
    print(f"\n📊 Processing Results:")
    print(f"   Total Processed: {len(results['processed_checks'])}")
    print(f"   Errors: {len(results['errors'])}")
    
    print(f"\n📈 Classification Summary:")
    for check_type, count in results['classification_summary'].items():
        print(f"   {check_type.title()}: {count} checks")
    
    print(f"\n📄 Generated PDFs:")
    for pdf_info in results['pdf_files']:
        file_size = os.path.getsize(pdf_info['path']) / 1024  # KB
        print(f"   {pdf_info['type'].title()}: {Path(pdf_info['path']).name} ({file_size:.1f} KB, {pdf_info['check_count']} checks)")
    
    # Show detailed results for each check
    print(f"\n📋 Detailed Check Analysis:")
    for i, check_info in enumerate(results['processed_checks']):
        classification = check_info['classification']
        original_name = Path(check_info['original_path']).name
        print(f"   {i+1}. {original_name}")
        print(f"      Type: {classification['type']} ({classification['confidence']:.1%} confidence)")
        print(f"      Size: {classification['dimensions']['width_inches']:.2f}\" x {classification['dimensions']['height_inches']:.2f}\"")
        print(f"      Aspect: {classification['dimensions']['aspect_ratio']:.2f}")
    
    # Check if PDFs use standard dimensions
    print(f"\n🎯 Verifying PDF Scaling:")
    for check_type in CheckClassifier.CHECK_TYPES:
        specs = CheckClassifier.CHECK_TYPES[check_type]
        print(f"   {check_type.title()}: Target {specs['width']}\" x {specs['height']}\" (aspect: {specs['aspect_ratio']:.2f})")
    
    print(f"\n✅ Test complete!")
    print(f"📁 Test images: {test_dir}")
    print(f"📁 Output PDFs: {output_dir}")
    
    # Clean up test images
    print(f"\n🧹 Cleaning up test images...")
    for filepath in test_paths:
        os.remove(filepath)
        print(f"   Removed: {Path(filepath).name}")
    os.rmdir(test_dir)

if __name__ == "__main__":
    test_complete_workflow()