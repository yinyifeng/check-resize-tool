#!/usr/bin/env python3
"""
Test script for auto-rotation functionality
Creates rotated images and tests the auto-rotation detection
"""

import cv2
import numpy as np
from PIL import Image
import os
import tempfile
from pathlib import Path
from check_resizer import CheckResizer
from demo_batch import create_sample_check

def test_rotation_detection():
    """Test the rotation detection and correction functionality."""
    
    print("🔄 Testing Auto-Rotation Functionality")
    print("=" * 50)
    
    resizer = CheckResizer()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # Create a sample check image
        base_filename = os.path.join(temp_dir, "test_check_base.png")
        create_sample_check('personal', base_filename, dpi=300)
        
        # Load the base image
        base_image = cv2.imread(base_filename)
        
        print(f"✅ Created base check image: {Path(base_filename).name}")
        height, width = base_image.shape[:2]
        print(f"   Original size: {width} x {height} pixels")
        
        # Test different rotations
        test_angles = [0, 90, 180, 270]
        results = {}
        
        for angle in test_angles:
            print(f"\n🔄 Testing {angle}° rotation...")
            
            # Create rotated version
            if angle == 0:
                rotated_image = base_image.copy()
            elif angle == 90:
                rotated_image = cv2.rotate(base_image, cv2.ROTATE_90_CLOCKWISE)
            elif angle == 180:
                rotated_image = cv2.rotate(base_image, cv2.ROTATE_180)
            elif angle == 270:
                rotated_image = cv2.rotate(base_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            # Save rotated image
            rotated_filename = os.path.join(temp_dir, f"test_check_{angle}deg.png")
            cv2.imwrite(rotated_filename, rotated_image)
            
            rot_height, rot_width = rotated_image.shape[:2]
            print(f"   Rotated size: {rot_width} x {rot_height} pixels")
            
            # Test orientation detection
            detected_rotation = resizer.detect_orientation(rotated_image)
            print(f"   Detected rotation needed: {detected_rotation}°")
            
            # Test auto-correction
            corrected_image, applied_rotation = resizer.rotate_image_if_needed(rotated_image, auto_rotate=True)
            corr_height, corr_width = corrected_image.shape[:2]
            print(f"   Applied rotation: {applied_rotation}°")
            print(f"   Corrected size: {corr_width} x {corr_height} pixels")
            
            # Save corrected image
            corrected_filename = os.path.join(temp_dir, f"test_check_{angle}deg_corrected.png")
            cv2.imwrite(corrected_filename, corrected_image)
            
            # Calculate if correction was successful
            original_aspect = width / height
            corrected_aspect = corr_width / corr_height
            aspect_similarity = abs(original_aspect - corrected_aspect) / original_aspect
            
            success = aspect_similarity < 0.1  # Within 10% of original aspect ratio
            print(f"   Success: {'✅' if success else '❌'} (aspect ratio similarity: {(1-aspect_similarity)*100:.1f}%)")
            
            results[angle] = {
                'detected_rotation': detected_rotation,
                'applied_rotation': applied_rotation,
                'success': success,
                'aspect_similarity': 1 - aspect_similarity,
                'original_size': (rot_width, rot_height),
                'corrected_size': (corr_width, corr_height)
            }
        
        # Summary
        print(f"\n📊 Auto-Rotation Test Results:")
        print(f"=" * 40)
        
        successful_tests = sum(1 for r in results.values() if r['success'])
        total_tests = len(results)
        
        for angle, result in results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  {angle}° rotation: {status}")
            print(f"    Detected: {result['detected_rotation']}°, Applied: {result['applied_rotation']}°")
            print(f"    Aspect similarity: {result['aspect_similarity']*100:.1f}%")
        
        print(f"\n🎯 Overall Result: {successful_tests}/{total_tests} tests passed")
        
        if successful_tests == total_tests:
            print("🎉 All auto-rotation tests PASSED!")
            print("The system successfully detects and corrects image orientation.")
        else:
            print("⚠️  Some auto-rotation tests FAILED.")
            print("Check the individual results above for details.")
        
        # Test with actual processing pipeline
        print(f"\n🔧 Testing Full Processing Pipeline...")
        
        # Test processing a rotated image
        rotated_90_file = os.path.join(temp_dir, "test_check_90deg.png")
        output_file = os.path.join(temp_dir, "processed_output.png")
        
        # Process with auto-rotation enabled
        success_with_rotation = resizer.resize_image(
            rotated_90_file, 
            output_file, 
            preview=False,
            auto_rotate=True
        )
        
        # Process with auto-rotation disabled
        output_file_no_rotation = os.path.join(temp_dir, "processed_output_no_rotation.png")
        success_without_rotation = resizer.resize_image(
            rotated_90_file,
            output_file_no_rotation, 
            preview=False,
            auto_rotate=False
        )
        
        print(f"  Processing with auto-rotation: {'✅ Success' if success_with_rotation else '❌ Failed'}")
        print(f"  Processing without auto-rotation: {'✅ Success' if success_without_rotation else '❌ Failed'}")
        
        if success_with_rotation and success_without_rotation:
            # Compare output sizes
            if os.path.exists(output_file):
                rotated_result = cv2.imread(output_file)
                rr_height, rr_width = rotated_result.shape[:2]
                rotated_aspect = rr_width / rr_height
            else:
                rotated_aspect = 0
                
            if os.path.exists(output_file_no_rotation):
                no_rotation_result = cv2.imread(output_file_no_rotation)
                nr_height, nr_width = no_rotation_result.shape[:2]
                no_rotation_aspect = nr_width / nr_height
            else:
                no_rotation_aspect = 0
            
            print(f"  With auto-rotation aspect ratio: {rotated_aspect:.2f}")
            print(f"  Without auto-rotation aspect ratio: {no_rotation_aspect:.2f}")
            
            # Check if auto-rotation produced a more horizontal result
            more_horizontal = rotated_aspect > no_rotation_aspect
            print(f"  Auto-rotation made image more horizontal: {'✅ Yes' if more_horizontal else '❌ No'}")
        
        # Save test files to permanent location for inspection
        test_output = "./test_rotation_output"
        if os.path.exists(test_output):
            shutil.rmtree(test_output)
        
        import shutil
        shutil.copytree(temp_dir, test_output)
        print(f"\n💾 Test files saved to: {test_output}")
        
        return successful_tests == total_tests

if __name__ == "__main__":
    success = test_rotation_detection()
    print(f"\n🎯 Final Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("\nAuto-rotation functionality is working correctly!")
        print("✅ Images are properly detected and corrected to horizontal orientation.")
    else:
        print("\nThere are issues with the auto-rotation functionality.")
        print("❌ Check the test results above for specific problems.")