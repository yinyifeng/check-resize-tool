#!/usr/bin/env python3
"""
Demo script for the Check Resizer Tool

This script creates sample check images and demonstrates the tool's capabilities.
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
from check_resizer import CheckResizer


def create_sample_check(filename, check_size=(600, 250), canvas_size=(800, 600), noise_level=0.1):
    """Create a realistic sample check image with whitespace."""
    
    # Create canvas with whitespace
    canvas = Image.new('RGB', canvas_size, 'white')
    draw = ImageDraw.Draw(canvas)
    
    # Calculate position to center the check with whitespace around it
    x_offset = (canvas_size[0] - check_size[0]) // 2
    y_offset = (canvas_size[1] - check_size[1]) // 2
    
    # Draw check background (slightly off-white)
    check_bg_color = (250, 250, 245)
    draw.rectangle([x_offset, y_offset, x_offset + check_size[0], y_offset + check_size[1]], 
                   fill=check_bg_color, outline='black', width=2)
    
    # Add check details
    text_color = 'black'
    
    # Bank name
    draw.text((x_offset + 20, y_offset + 20), "SAMPLE BANK", fill=text_color)
    
    # Address
    draw.text((x_offset + 20, y_offset + 40), "123 Banking Street", fill=text_color)
    draw.text((x_offset + 20, y_offset + 55), "Finance City, FC 12345", fill=text_color)
    
    # Check number
    draw.text((x_offset + 400, y_offset + 20), "Check #: 1001", fill=text_color)
    
    # Date
    draw.text((x_offset + 400, y_offset + 50), "Date: 11/13/2025", fill=text_color)
    
    # Pay to the order of
    draw.text((x_offset + 20, y_offset + 100), "Pay to the order of:", fill=text_color)
    draw.line([x_offset + 150, y_offset + 115, x_offset + 550, y_offset + 115], fill=text_color, width=1)
    
    # Amount box
    draw.rectangle([x_offset + 450, y_offset + 130, x_offset + 580, y_offset + 155], 
                   outline=text_color, width=1)
    draw.text((x_offset + 460, y_offset + 135), "$ 100.00", fill=text_color)
    
    # Amount in words
    draw.line([x_offset + 20, y_offset + 155, x_offset + 440, y_offset + 155], fill=text_color, width=1)
    draw.text((x_offset + 20, y_offset + 140), "One hundred dollars and 00/100", fill=text_color)
    
    # Memo
    draw.text((x_offset + 20, y_offset + 180), "Memo:", fill=text_color)
    draw.line([x_offset + 70, y_offset + 195, x_offset + 300, y_offset + 195], fill=text_color, width=1)
    
    # Signature line
    draw.text((x_offset + 350, y_offset + 180), "Signature:", fill=text_color)
    draw.line([x_offset + 420, y_offset + 195, x_offset + 570, y_offset + 195], fill=text_color, width=1)
    
    # Account numbers at bottom
    draw.text((x_offset + 20, y_offset + 220), ":123456789: 1234567890 1001", fill=text_color)
    
    # Add some noise to make it more realistic
    if noise_level > 0:
        import random
        for _ in range(int(canvas_size[0] * canvas_size[1] * noise_level / 1000)):
            x = random.randint(0, canvas_size[0] - 1)
            y = random.randint(0, canvas_size[1] - 1)
            draw.point((x, y), fill=(200, 200, 200))
    
    canvas.save(filename)
    print(f"Created sample check: {filename}")


def run_demo():
    """Run a complete demonstration of the check resizer tool."""
    
    print("Check Resizer Tool - Demo")
    print("=" * 30)
    
    # Create demo directory
    demo_dir = Path("demo_images")
    demo_dir.mkdir(exist_ok=True)
    
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)
    
    # Create sample check images with different characteristics
    samples = [
        ("demo_check_1.png", (600, 250), (900, 700), 0.05),  # Lots of whitespace
        ("demo_check_2.png", (500, 200), (800, 600), 0.1),   # Medium whitespace
        ("demo_check_3.png", (550, 230), (750, 550), 0.02),  # Clean scan
        ("demo_check_4.png", (580, 240), (1000, 800), 0.15), # Large canvas
    ]
    
    print(f"\nCreating {len(samples)} sample check images...")
    for filename, check_size, canvas_size, noise in samples:
        create_sample_check(demo_dir / filename, check_size, canvas_size, noise)
    
    print(f"\nProcessing images with CheckResizer...")
    print("-" * 40)
    
    # Initialize resizer
    resizer = CheckResizer()
    
    # Process each sample
    for filename, _, _, _ in samples:
        input_path = demo_dir / filename
        output_path = output_dir / f"resized_{filename}"
        
        print(f"\nProcessing {filename}:")
        success = resizer.resize_image(input_path, output_path)
        
        if success:
            # Show file size comparison
            original_size = input_path.stat().st_size
            new_size = output_path.stat().st_size
            size_reduction = (original_size - new_size) / original_size * 100
            
            print(f"  Original size: {original_size:,} bytes")
            print(f"  New size: {new_size:,} bytes")
            print(f"  Size reduction: {size_reduction:.1f}%")
    
    print(f"\nDemo completed!")
    print(f"Original images saved in: {demo_dir}")
    print(f"Processed images saved in: {output_dir}")
    print(f"\nTo clean up demo files, run:")
    print(f"  rm -rf {demo_dir} {output_dir}")
    
    print(f"\nNext steps:")
    print(f"1. Try processing your own check images:")
    print(f"   python check_resizer.py your_check.jpg --preview")
    print(f"2. Process a folder of checks:")
    print(f"   python check_resizer.py your_folder/ --batch")


if __name__ == "__main__":
    run_demo()