#!/usr/bin/env python3
"""
Demo script for Check Batch Processor
Creates sample check images and demonstrates the batch processing workflow
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile
import shutil
from pathlib import Path
from check_batch_processor import CheckBatchProcessor
import random

def create_sample_check(check_type: str, filename: str, dpi: int = 300) -> str:
    """Create a sample check image for testing."""
    
    # Define check dimensions (in pixels at given DPI)
    dimensions = {
        'personal': (int(6.0 * dpi), int(2.75 * dpi)),    # 6" x 2.75"
        'business': (int(8.5 * dpi), int(3.5 * dpi)),     # 8.5" x 3.5" 
        'commercial': (int(8.5 * dpi), int(11.0 * dpi))   # 8.5" x 11"
    }
    
    width, height = dimensions.get(check_type, dimensions['personal'])
    
    # Create blank check image
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, fall back to default if not available
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size=int(24 * dpi/150))
        font_medium = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size=int(18 * dpi/150))
        font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size=int(12 * dpi/150))
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw check elements based on type
    margin = int(0.2 * dpi)  # 0.2" margin
    
    if check_type == 'personal':
        # Personal check layout
        # Bank name
        draw.text((margin, margin), "FIRST NATIONAL BANK", fill='black', font=font_medium)
        
        # Check number
        check_num = f"#{random.randint(1001, 9999)}"
        draw.text((width - margin - 100, margin), check_num, fill='black', font=font_small)
        
        # Pay to line
        pay_y = int(height * 0.4)
        draw.text((margin, pay_y), "Pay to the order of:", fill='black', font=font_small)
        draw.line([(margin + 150, pay_y + 25), (width - margin, pay_y + 25)], fill='black', width=1)
        
        # Amount box
        amount_box = (width - 150, pay_y - 10, width - margin, pay_y + 30)
        draw.rectangle(amount_box, outline='black', width=2)
        draw.text((amount_box[0] + 5, pay_y), "$", fill='black', font=font_medium)
        
        # Memo line
        memo_y = int(height * 0.7)
        draw.text((margin, memo_y), "Memo:", fill='black', font=font_small)
        draw.line([(margin + 50, memo_y + 15), (width - 200, memo_y + 15)], fill='black', width=1)
        
        # Signature line
        draw.line([(width - 180, memo_y + 15), (width - margin, memo_y + 15)], fill='black', width=1)
        
    elif check_type == 'business':
        # Business check layout
        # Company name
        draw.text((margin, margin), "ACME CORPORATION", fill='black', font=font_large)
        draw.text((margin, margin + 30), "123 Business Ave, Suite 100", fill='black', font=font_small)
        draw.text((margin, margin + 45), "Business City, ST 12345", fill='black', font=font_small)
        
        # Check number
        check_num = f"Check #{random.randint(10001, 99999)}"
        draw.text((width - margin - 150, margin), check_num, fill='black', font=font_medium)
        
        # Date line
        date_y = margin + 60
        draw.text((width - 200, date_y), "Date:", fill='black', font=font_small)
        draw.line([(width - 150, date_y + 15), (width - margin, date_y + 15)], fill='black', width=1)
        
        # Pay to line
        pay_y = int(height * 0.45)
        draw.text((margin, pay_y), "Pay to the order of:", fill='black', font=font_small)
        draw.line([(margin + 150, pay_y + 25), (width - 200, pay_y + 25)], fill='black', width=1)
        
        # Amount
        draw.text((width - 180, pay_y), "Amount: $", fill='black', font=font_small)
        draw.line([(width - 120, pay_y + 15), (width - margin, pay_y + 15)], fill='black', width=1)
        
        # Signature
        sig_y = int(height * 0.75)
        draw.text((width - 200, sig_y), "Authorized Signature:", fill='black', font=font_small)
        draw.line([(width - 200, sig_y + 20), (width - margin, sig_y + 20)], fill='black', width=2)
        
    else:  # commercial
        # Commercial check with voucher
        # Top portion - check
        check_height = int(height * 0.3)
        
        # Company header
        draw.text((margin, margin), "ENTERPRISE SOLUTIONS INC.", fill='black', font=font_large)
        draw.text((margin, margin + 35), "Corporate Headquarters", fill='black', font=font_medium)
        
        # Check details
        check_y = margin + 80
        draw.text((margin, check_y), f"Check #: {random.randint(100001, 999999)}", fill='black', font=font_medium)
        
        # Pay line
        pay_y = check_y + 40
        draw.text((margin, pay_y), "Pay:", fill='black', font=font_small)
        draw.line([(margin + 40, pay_y + 20), (width - 150, pay_y + 20)], fill='black', width=1)
        
        # Amount
        draw.rectangle((width - 140, pay_y, width - margin, pay_y + 30), outline='black', width=2)
        
        # Voucher section
        voucher_y = check_height + 50
        draw.line([(0, voucher_y - 20), (width, voucher_y - 20)], fill='black', width=2)
        draw.text((margin, voucher_y), "REMITTANCE ADVICE", fill='black', font=font_large)
        
        # Voucher details
        draw.text((margin, voucher_y + 50), "Invoice #", fill='black', font=font_small)
        draw.text((margin + 100, voucher_y + 50), "Description", fill='black', font=font_small)
        draw.text((margin + 300, voucher_y + 50), "Amount", fill='black', font=font_small)
        
        # Sample line items
        for i in range(3):
            line_y = voucher_y + 80 + (i * 25)
            draw.text((margin, line_y), f"INV-{1000 + i}", fill='black', font=font_small)
            draw.text((margin + 100, line_y), f"Service #{i+1}", fill='black', font=font_small)
            draw.text((margin + 300, line_y), f"${random.randint(100, 999)}.00", fill='black', font=font_small)
    
    # Add some realistic imperfections
    # Slight rotation
    if random.random() > 0.3:  # Increased chance of rotation for demo
        angle = random.uniform(-15, 15)  # Larger rotation range
        image = image.rotate(angle, expand=True, fillcolor='white')
    
    # Add some margin/padding to simulate scanning
    padding = int(0.3 * dpi)  # 0.3" padding
    padded_width = image.width + 2 * padding
    padded_height = image.height + 2 * padding
    
    padded_image = Image.new('RGB', (padded_width, padded_height), color='lightgray')
    paste_x = (padded_width - image.width) // 2
    paste_y = (padded_height - image.height) // 2
    padded_image.paste(image, (paste_x, paste_y))
    
    # Randomly apply 90-degree rotations to simulate phone photos
    if random.random() > 0.7:  # 30% chance
        rotation_steps = random.choice([1, 2, 3])  # 90, 180, or 270 degrees
        for _ in range(rotation_steps):
            padded_image = padded_image.rotate(90, expand=True)
    
    # Save image
    padded_image.save(filename, 'PNG', dpi=(dpi, dpi))
    return filename

def create_sample_batch(output_dir: str, num_checks: int = 12) -> list:
    """Create a batch of sample check images."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    check_types = ['personal', 'business', 'commercial']
    image_paths = []
    
    for i in range(num_checks):
        # Randomly select check type (weighted towards personal/business)
        weights = [0.5, 0.3, 0.2]  # 50% personal, 30% business, 20% commercial
        check_type = random.choices(check_types, weights=weights)[0]
        
        # Vary DPI slightly to test classification
        dpi = random.choice([200, 250, 300, 350, 400])
        
        filename = os.path.join(output_dir, f"sample_check_{i+1:02d}_{check_type}.png")
        create_sample_check(check_type, filename, dpi)
        image_paths.append(filename)
        
        print(f"Created: {Path(filename).name} ({check_type}, {dpi} DPI)")
    
    return image_paths

def main():
    """Demonstrate the batch processing workflow."""
    
    print("🚀 Check Batch Processor Demo")
    print("=" * 50)
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # Create sample images
        print("\n📋 Creating sample check images...")
        sample_dir = os.path.join(temp_dir, "samples")
        image_paths = create_sample_batch(sample_dir, num_checks=9)
        
        print(f"\n✅ Created {len(image_paths)} sample checks")
        
        # Process the batch
        print("\n🔄 Processing batch...")
        processor = CheckBatchProcessor()
        output_dir = os.path.join(temp_dir, "output")
        
        results = processor.process_batch(image_paths, output_dir)
        
        # Display results
        print(f"\n📊 Processing Results:")
        print(f"  Total Processed: {len(results['processed_checks'])}")
        print(f"  Errors: {len(results['errors'])}")
        print(f"  PDF Files Generated: {len(results['pdf_files'])}")
        
        print(f"\n📈 Classification Summary:")
        for check_type, count in results['classification_summary'].items():
            print(f"  {check_type.title()}: {count} checks")
        
        print(f"\n📄 Generated PDFs:")
        for pdf_info in results['pdf_files']:
            pdf_size = os.path.getsize(pdf_info['path']) / 1024  # KB
            print(f"  {pdf_info['type'].title()}: {Path(pdf_info['path']).name} ({pdf_size:.1f} KB)")
        
        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"  • {error}")
        
        # Save demo files to a permanent location for inspection
        demo_output = "./demo_batch_output"
        if os.path.exists(demo_output):
            shutil.rmtree(demo_output)
        
        shutil.copytree(output_dir, demo_output)
        shutil.copytree(sample_dir, os.path.join(demo_output, "sample_images"))
        
        print(f"\n💾 Demo files saved to: {demo_output}")
        print("🎉 Demo complete!")

if __name__ == "__main__":
    main()