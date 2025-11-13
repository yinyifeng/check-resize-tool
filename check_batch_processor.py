#!/usr/bin/env python3
"""
Check Batch Processor with Auto-Classification and Print Layout
Processes multiple check images, classifies them by type, and creates print-ready PDFs
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
import io
from sklearn.cluster import KMeans
from check_resizer import CheckResizer

class CheckClassifier:
    """Automatically classify checks by type based on size and features."""
    
    # Standard check dimensions in inches (approximate)
    CHECK_TYPES = {
        'personal': {
            'width': 6.0,    # Personal checks: ~6" x 2.75"
            'height': 2.75,
            'aspect_ratio': 2.18,
            'tolerance': 0.3
        },
        'business': {
            'width': 8.5,    # Business checks: ~8.5" x 3.5" 
            'height': 3.5,
            'aspect_ratio': 2.43,
            'tolerance': 0.3
        },
        'commercial': {
            'width': 8.5,    # Commercial checks: ~8.5" x 11" (voucher style)
            'height': 11.0,
            'aspect_ratio': 0.77,
            'tolerance': 0.4
        }
    }
    
    def __init__(self):
        self.dpi_estimate = 300  # Default DPI for classification
    
    def estimate_dpi(self, image: np.ndarray) -> float:
        """Estimate DPI based on image size and assumed check type."""
        height, width = image.shape[:2]
        
        # Try to match against known check types
        best_dpi = 300
        min_error = float('inf')
        
        for check_type, dims in self.CHECK_TYPES.items():
            for dpi in [150, 200, 300, 400, 600]:
                expected_width = dims['width'] * dpi
                expected_height = dims['height'] * dpi
                
                width_error = abs(width - expected_width) / expected_width
                height_error = abs(height - expected_height) / expected_height
                total_error = width_error + height_error
                
                if total_error < min_error:
                    min_error = total_error
                    best_dpi = dpi
        
        return best_dpi
    
    def classify_check(self, image: np.ndarray, filename: str = "") -> Dict:
        """Classify a check image by type."""
        height, width = image.shape[:2]
        
        # Estimate DPI
        estimated_dpi = self.estimate_dpi(image)
        
        # Calculate physical dimensions
        width_inches = width / estimated_dpi
        height_inches = height / estimated_dpi
        aspect_ratio = width_inches / height_inches
        
        # Find best matching check type
        best_match = None
        best_score = float('inf')
        
        for check_type, specs in self.CHECK_TYPES.items():
            width_diff = abs(width_inches - specs['width']) / specs['width']
            height_diff = abs(height_inches - specs['height']) / specs['height']
            aspect_diff = abs(aspect_ratio - specs['aspect_ratio']) / specs['aspect_ratio']
            
            score = width_diff + height_diff + aspect_diff
            
            if score < best_score and score < specs['tolerance']:
                best_score = score
                best_match = check_type
        
        # If no match, use aspect ratio to guess
        if best_match is None:
            if aspect_ratio > 2.0:
                best_match = 'personal' if width_inches < 7 else 'business'
            else:
                best_match = 'commercial'
        
        return {
            'type': best_match,
            'confidence': max(0, 1 - best_score) if best_match else 0.5,
            'dimensions': {
                'width_pixels': width,
                'height_pixels': height,
                'width_inches': round(width_inches, 2),
                'height_inches': round(height_inches, 2),
                'aspect_ratio': round(aspect_ratio, 2),
                'estimated_dpi': estimated_dpi
            },
            'filename': filename
        }

class CheckBatchProcessor:
    """Process multiple checks and create print-ready layouts."""
    
    def __init__(self):
        self.resizer = CheckResizer()
        self.classifier = CheckClassifier()
        
        # Print layout settings
        self.print_settings = {
            'page_size': letter,  # 8.5" x 11"
            'margin': 0.5,        # 0.5" margins
            'checks_per_page': 3,
            'spacing': 0.25       # 0.25" between checks
        }
    
    def process_batch(self, image_paths: List[str], output_dir: str) -> Dict:
        """Process a batch of check images."""
        
        print("🔄 Processing batch of check images...")
        print(f"📁 Input: {len(image_paths)} images")
        print(f"📁 Output directory: {output_dir}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Process each image
        results = {
            'processed_checks': [],
            'classification_summary': {},
            'errors': [],
            'pdf_files': []
        }
        
        processed_images = []
        
        for i, image_path in enumerate(image_paths):
            try:
                print(f"\n📋 Processing {i+1}/{len(image_paths)}: {Path(image_path).name}")
                
                # Load and process image
                image = cv2.imread(image_path)
                if image is None:
                    raise ValueError(f"Could not load image: {image_path}")
                
                # Resize/crop the image
                temp_output = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                success = self.resizer.resize_image(
                    image_path, 
                    temp_output.name,
                    preview=False,
                    level_background=True,
                    level_method='gaussian',
                    level_intensity='gentle'
                )
                
                if not success:
                    print(f"  ⚠️  Auto-resize failed, using original")
                    # Use original if auto-resize fails
                    processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    temp_output = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                    Image.fromarray(processed_image).save(temp_output.name)
                else:
                    print(f"  ✅ Auto-resized successfully")
                
                # Load processed image for classification
                processed_image = cv2.imread(temp_output.name)
                
                # Classify check type
                classification = self.classifier.classify_check(
                    processed_image, 
                    Path(image_path).name
                )
                
                print(f"  📊 Type: {classification['type']} (confidence: {classification['confidence']:.0%})")
                print(f"  📏 Size: {classification['dimensions']['width_inches']}\" x {classification['dimensions']['height_inches']}\"")
                
                # Store results
                check_info = {
                    'original_path': image_path,
                    'processed_path': temp_output.name,
                    'classification': classification
                }
                
                processed_images.append(check_info)
                results['processed_checks'].append(check_info)
                
                # Update summary
                check_type = classification['type']
                if check_type not in results['classification_summary']:
                    results['classification_summary'][check_type] = 0
                results['classification_summary'][check_type] += 1
                
            except Exception as e:
                error_msg = f"Error processing {image_path}: {str(e)}"
                print(f"  ❌ {error_msg}")
                results['errors'].append(error_msg)
        
        # Group by check type and create PDFs
        print(f"\n📊 Classification Summary:")
        for check_type, count in results['classification_summary'].items():
            print(f"  {check_type.title()}: {count} checks")
        
        # Create PDFs grouped by type
        grouped_checks = self._group_checks_by_type(processed_images)
        
        for check_type, checks in grouped_checks.items():
            if checks:
                pdf_path = self._create_print_pdf(checks, check_type, output_dir)
                results['pdf_files'].append({
                    'type': check_type,
                    'path': pdf_path,
                    'check_count': len(checks)
                })
                print(f"  📄 Created {check_type} PDF: {Path(pdf_path).name}")
        
        # Create summary report
        self._create_summary_report(results, output_dir)
        
        return results
    
    def _group_checks_by_type(self, processed_images: List[Dict]) -> Dict[str, List[Dict]]:
        """Group processed checks by type."""
        grouped = {}
        
        for check_info in processed_images:
            check_type = check_info['classification']['type']
            if check_type not in grouped:
                grouped[check_type] = []
            grouped[check_type].append(check_info)
        
        return grouped
    
    def _create_print_pdf(self, checks: List[Dict], check_type: str, output_dir: str) -> str:
        """Create a print-ready PDF with 3 checks per page."""
        
        pdf_filename = f"{check_type}_checks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        # PDF setup
        page_width, page_height = self.print_settings['page_size']
        margin = self.print_settings['margin'] * 72  # Convert to points
        spacing = self.print_settings['spacing'] * 72
        
        usable_width = page_width - 2 * margin
        usable_height = page_height - 2 * margin
        
        # Calculate check dimensions for layout
        checks_per_page = self.print_settings['checks_per_page']
        check_height = (usable_height - (checks_per_page - 1) * spacing) / checks_per_page
        
        c = canvas.Canvas(pdf_path, pagesize=self.print_settings['page_size'])
        
        for i, check_info in enumerate(checks):
            if i % checks_per_page == 0 and i > 0:
                c.showPage()  # New page
            
            position_on_page = i % checks_per_page
            y_offset = page_height - margin - (position_on_page * (check_height + spacing)) - check_height
            
            # Load and scale image
            try:
                pil_image = Image.open(check_info['processed_path'])
                
                # Calculate scaling to fit width
                scale = usable_width / pil_image.width
                scaled_width = usable_width
                scaled_height = pil_image.height * scale
                
                # If too tall, scale to fit height instead
                if scaled_height > check_height:
                    scale = check_height / pil_image.height
                    scaled_height = check_height
                    scaled_width = pil_image.width * scale
                
                # Center horizontally
                x_offset = margin + (usable_width - scaled_width) / 2
                
                # Draw image
                c.drawImage(
                    ImageReader(pil_image),
                    x_offset, y_offset,
                    width=scaled_width,
                    height=scaled_height,
                    preserveAspectRatio=True
                )
                
                # Add filename label
                c.setFont("Helvetica", 8)
                c.drawString(
                    x_offset, y_offset - 12,
                    f"{Path(check_info['original_path']).name}"
                )
                
            except Exception as e:
                # Draw error placeholder
                c.setFillColor("red")
                c.rect(margin, y_offset, usable_width, check_height)
                c.setFillColor("white")
                c.setFont("Helvetica", 12)
                c.drawCentredText(
                    page_width / 2, y_offset + check_height / 2,
                    f"Error loading: {Path(check_info['original_path']).name}"
                )
        
        # Add page numbers and metadata
        page_count = (len(checks) + checks_per_page - 1) // checks_per_page
        for page_num in range(1, page_count + 1):
            if page_num > 1:
                c.showPage()
            
            c.setFont("Helvetica", 10)
            c.drawRightString(
                page_width - margin, margin / 2,
                f"Page {page_num} of {page_count} | {check_type.title()} Checks"
            )
        
        c.save()
        return pdf_path
    
    def _create_summary_report(self, results: Dict, output_dir: str):
        """Create a summary report of the batch processing."""
        
        report_path = os.path.join(output_dir, "batch_summary.json")
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_processed': len(results['processed_checks']),
            'total_errors': len(results['errors']),
            'classification_summary': results['classification_summary'],
            'pdf_files': results['pdf_files'],
            'errors': results['errors']
        }
        
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Also create a readable text report
        text_report_path = os.path.join(output_dir, "batch_summary.txt")
        with open(text_report_path, 'w') as f:
            f.write("Check Batch Processing Summary\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Images: {len(results['processed_checks'])}\n")
            f.write(f"Errors: {len(results['errors'])}\n\n")
            
            f.write("Classification Results:\n")
            f.write("-" * 25 + "\n")
            for check_type, count in results['classification_summary'].items():
                f.write(f"{check_type.title()}: {count} checks\n")
            
            f.write(f"\nGenerated PDF Files:\n")
            f.write("-" * 20 + "\n")
            for pdf_info in results['pdf_files']:
                f.write(f"{pdf_info['type'].title()}: {Path(pdf_info['path']).name} ({pdf_info['check_count']} checks)\n")
            
            if results['errors']:
                f.write(f"\nErrors:\n")
                f.write("-" * 8 + "\n")
                for error in results['errors']:
                    f.write(f"• {error}\n")

def main():
    """Example usage of the batch processor."""
    
    print("🚀 Check Batch Processor")
    print("=" * 40)
    
    # Example usage
    processor = CheckBatchProcessor()
    
    # Example image paths (replace with actual paths)
    sample_images = [
        "/path/to/check1.png",
        "/path/to/check2.jpg",
        "/path/to/check3.pdf"
    ]
    
    output_directory = "./batch_output"
    
    try:
        results = processor.process_batch(sample_images, output_directory)
        
        print("\n🎉 Batch Processing Complete!")
        print(f"📁 Results saved to: {output_directory}")
        print(f"📊 Processed: {len(results['processed_checks'])} checks")
        print(f"📄 Generated: {len(results['pdf_files'])} PDF files")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()