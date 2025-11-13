# Check Batch Processor

Automatically process multiple check images with classification and print-ready PDF generation.

## Features

### 🔍 Automatic Classification
- **Personal Checks**: ~6" × 2.75" (standard personal check size)
- **Business Checks**: ~8.5" × 3.5" (business check size)
- **Commercial Checks**: ~8.5" × 11" (voucher-style with detach)

### 🖼️ Image Processing
- Automatic cropping and whitespace removal
- **Auto-rotation detection and correction** for proper horizontal orientation
- Background leveling (remove paper texture/shadows)
- Multiple detection algorithms with fallbacks
- Handles various image formats (PNG, JPG, TIFF, BMP)

### 📄 Print Layout Generation
- Groups checks by type automatically
- Configurable checks per page (1-4)
- Professional PDF layout with proper margins
- Maintains aspect ratios and print quality
- Page numbering and metadata

### 🌐 User Interface
- Drag-and-drop batch upload
- Real-time processing progress
- Preview and download options
- Detailed processing reports

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Batch Processor UI
```bash
python start_batch_processor.py
```

### 3. Upload and Process
1. Upload multiple check images via drag-and-drop
2. Configure processing settings (background leveling, checks per page)
3. Click "Process Batch"
4. Download generated PDFs grouped by check type

## Command Line Usage

### Process Files Programmatically
```python
from check_batch_processor import CheckBatchProcessor

processor = CheckBatchProcessor()
results = processor.process_batch(
    image_paths=['/path/to/check1.png', '/path/to/check2.jpg'],
    output_dir='./output'
)
```

### Create Demo/Test Data
```bash
python demo_batch.py
```
This creates sample check images and demonstrates the full workflow.

## Configuration Options

### Processing Settings
- **Background Leveling**: Remove paper background
- **Level Intensity**: gentle/medium/strong
- **Level Method**: gaussian/morphological/polynomial
- **Checks Per Page**: 1-4 checks per printed page

### Classification Algorithm
The system automatically detects check types using:
- Aspect ratio analysis
- Size estimation
- Pattern recognition
- DPI calculation

### Print Layout
- **Page Size**: US Letter (8.5" × 11")
- **Margins**: 0.5" on all sides
- **Spacing**: 0.25" between checks
- **Quality**: Maintains original resolution
- **Metadata**: Filenames, page numbers, timestamps

## Output Structure

```
output/
├── personal_checks_20241113_143052.pdf     # Personal checks PDF
├── business_checks_20241113_143052.pdf     # Business checks PDF
├── commercial_checks_20241113_143052.pdf   # Commercial checks PDF
├── batch_summary.json                      # Machine-readable results
└── batch_summary.txt                       # Human-readable summary
```

### PDF Contents
- **3 checks per page** (configurable)
- **Filename labels** below each check
- **Page numbers** and metadata
- **High-quality scaling** preserving aspect ratios

### Summary Reports
- Processing timestamp
- Classification breakdown
- Individual file results
- Error reporting
- Confidence scores

## Troubleshooting

### Download Issues
If you're having trouble downloading PDFs from the web interface:

1. **Try the alternative download server**:
   ```bash
   python download_server.py --directory demo_batch_output
   ```
   This starts a simple file server at http://localhost:8503

2. **Check file locations manually**:
   - Demo output: `./demo_batch_output/`
   - Test output: `./test_batch_output/` 
   - Processing output: Usually in system temp directory

3. **Verify functionality with test**:
   ```bash
   python test_pdf_downloads.py
   ```

### Classification Issues
- **Low Confidence**: Check may be rotated, cropped, or unusual size
- **Wrong Type**: Manual verification recommended for edge cases
- **Unrecognized**: Falls back to aspect ratio classification

### Processing Errors
- **File Loading**: Ensure images are valid formats
- **Memory**: Large batches may require processing in chunks
- **Background Leveling**: Disable if causing distortion

### Print Quality
- **Resolution**: Original resolution maintained
- **Scaling**: Automatic scaling to fit page layout
- **Orientation**: Maintains original check orientation

## Technical Details

### Classification Algorithm
1. **Size Analysis**: Calculate physical dimensions from pixels
2. **DPI Estimation**: Match against standard check sizes
3. **Aspect Ratio**: Primary classification feature
4. **Confidence Scoring**: Based on deviation from standards

### Supported Check Types
| Type | Dimensions | Aspect Ratio | Usage |
|------|------------|--------------|-------|
| Personal | 6" × 2.75" | 2.18:1 | Individual banking |
| Business | 8.5" × 3.5" | 2.43:1 | Business payments |
| Commercial | 8.5" × 11" | 0.77:1 | Voucher with stub |

### Processing Pipeline
1. **Load Images**: Batch file handling
2. **Auto-Crop**: Remove whitespace using multiple algorithms
3. **Background Level**: Optional paper texture removal
4. **Classify**: Determine check type and confidence
5. **Group**: Organize by type for printing
6. **Layout**: Create print-ready PDFs
7. **Report**: Generate summary and metadata

## Integration

### With Existing Check Resizer
The batch processor extends the existing `CheckResizer` class:
```python
# Individual processing
resizer = CheckResizer()
resizer.resize_image('input.png', 'output.png')

# Batch processing
processor = CheckBatchProcessor()  # Uses CheckResizer internally
results = processor.process_batch(image_paths, output_dir)
```

### API Integration
```python
# Customize settings
processor = CheckBatchProcessor()
processor.print_settings['checks_per_page'] = 4
processor.print_settings['margin'] = 0.75  # Larger margins

# Override classification
custom_types = {'check1.png': 'business', 'check2.png': 'personal'}
# (Manual override feature could be added)
```

## Future Enhancements

### Planned Features
- [ ] Manual classification override
- [ ] Custom check sizes/types
- [ ] Batch orientation correction
- [ ] OCR for metadata extraction
- [ ] Integration with banking systems
- [ ] Quality assessment scoring

### Advanced Options
- [ ] Custom PDF templates
- [ ] Watermarking support
- [ ] Encrypted PDF output
- [ ] Audit trail logging
- [ ] Performance monitoring

## Support

### File Requirements
- **Formats**: PNG, JPG, JPEG, TIFF, BMP
- **Size**: No specific limits (memory dependent)
- **Quality**: Higher resolution improves classification
- **Orientation**: Any orientation supported

### System Requirements
- **Python**: 3.8+ required
- **Memory**: 2GB+ recommended for large batches
- **Storage**: Temporary space for processing
- **Display**: Web browser for UI

### Dependencies
- OpenCV: Image processing
- ReportLab: PDF generation
- Streamlit: Web interface
- Scikit-learn: Classification algorithms
- NumPy/Pillow: Image handling