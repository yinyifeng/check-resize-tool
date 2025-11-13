#!/usr/bin/env python3
"""
Example usage of the Check Resizer Tool

This script demonstrates how to use the CheckResizer class programmatically.
"""

from check_resizer import CheckResizer
import os
from pathlib import Path


def create_sample_usage():
    """Example of how to use the CheckResizer class."""
    
    # Initialize the resizer
    resizer = CheckResizer()
    
    # Example 1: Process a single image
    print("Example 1: Single image processing")
    print("-" * 40)
    
    # You would replace this with your actual image path
    sample_image = "path/to/your/check_image.jpg"
    
    if os.path.exists(sample_image):
        # Process with preview
        resizer.resize_image(sample_image, preview=True)
        
        # Process and save to specific location
        output_path = "processed_check.jpg"
        resizer.resize_image(sample_image, output_path)
        print(f"Processed image saved to: {output_path}")
    else:
        print(f"Sample image not found: {sample_image}")
        print("Please provide a valid check image path")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Batch process a directory
    print("Example 2: Batch processing")
    print("-" * 40)
    
    input_directory = "input_checks"
    output_directory = "processed_checks"
    
    # Create sample directory structure (commented out - uncomment to use)
    # Path(input_directory).mkdir(exist_ok=True)
    # Path(output_directory).mkdir(exist_ok=True)
    
    if os.path.exists(input_directory):
        resizer.batch_resize(input_directory, output_directory, preview=False)
    else:
        print(f"Input directory not found: {input_directory}")
        print("Create the directory and add some check images to test batch processing")
    
    print("\nUsage examples completed!")


def print_usage_instructions():
    """Print detailed usage instructions."""
    
    print("Check Resizer Tool - Usage Instructions")
    print("=" * 50)
    print()
    
    print("Command Line Usage:")
    print("------------------")
    print()
    print("1. Process a single image:")
    print("   python check_resizer.py input_image.jpg")
    print("   python check_resizer.py input_image.jpg -o output_image.jpg")
    print()
    
    print("2. Process a single image with preview:")
    print("   python check_resizer.py input_image.jpg --preview")
    print()
    
    print("3. Batch process all images in a directory:")
    print("   python check_resizer.py input_folder/ --batch")
    print("   python check_resizer.py input_folder/ --batch -o output_folder/")
    print()
    
    print("4. Batch process with preview (for small batches):")
    print("   python check_resizer.py input_folder/ --batch --preview")
    print()
    
    print("Programmatic Usage:")
    print("------------------")
    print("""
from check_resizer import CheckResizer

# Initialize
resizer = CheckResizer()

# Process single image
resizer.resize_image('check.jpg', 'cropped_check.jpg', preview=True)

# Batch process
resizer.batch_resize('input_dir/', 'output_dir/')
    """)
    
    print("Supported Image Formats:")
    print("-----------------------")
    print("JPG, JPEG, PNG, BMP, TIFF, TIF")
    print()
    
    print("Features:")
    print("---------")
    print("• Automatic edge detection using multiple algorithms")
    print("• Intelligent boundary detection for check content")
    print("• Preserves image quality while removing whitespace")
    print("• Batch processing support")
    print("• Preview functionality")
    print("• Configurable output paths")


if __name__ == "__main__":
    print_usage_instructions()
    print("\n" + "="*60 + "\n")
    create_sample_usage()