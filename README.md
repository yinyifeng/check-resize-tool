# Check Resize Tool

A comprehensive Python tool for automatically analyzing, resizing, and processing check images with automatic classification and print layout generation.

## 🌟 Features

### Individual Check Processing
- **Web Interface**: User-friendly web UI for drag-and-drop image processing
- **Auto-Rotation**: Automatic detection and correction of image orientation to horizontal
- **Background Leveling**: Remove background variations, shadows, and uneven lighting
- **Automatic Edge Detection**: Uses multiple computer vision algorithms (Canny edge detection, adaptive thresholding, morphological operations) to find optimal crop boundaries
- **Intelligent Cropping**: Automatically detects check boundaries and removes whitespace while preserving all important content
- **Multiple Processing Methods**: Employs different algorithms and selects the best result for each image
- **Preview Functionality**: See before/after comparisons before saving
- **High Quality Output**: Maintains image quality while reducing file size
- **Flexible Input/Output**: Support for various image formats and custom output paths

### 🆕 Batch Processing (NEW!)
- **Automatic Classification**: Identifies Personal, Business, and Commercial checks
- **Auto-Rotation**: Detects and corrects orientation for all uploaded images
- **Bulk Upload**: Process multiple check images simultaneously  
- **Print Layout Generation**: Creates print-ready PDFs with 3 checks per page
- **Smart Grouping**: Automatically groups checks by type for organized output
- **Professional PDFs**: Generates publication-ready documents with proper margins and scaling
- **Progress Tracking**: Real-time processing status and detailed reporting
- **Download Management**: Individual or bulk download of processed files

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository:
```bash
git clone https://github.com/yinyifeng/check-resize-tool.git
cd check-resize-tool
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
check-resize-tool/
├── ui.py                       # Individual check processing UI
├── batch_ui.py                 # NEW: Batch processing UI
├── start_check_resizer.py      # Launcher for individual processing
├── start_batch_processor.py    # NEW: Launcher for batch processing
├── check_resizer.py            # Core processing engine
├── check_batch_processor.py    # NEW: Batch processing engine
├── demo_batch.py              # NEW: Batch processing demo
├── test_pdf_downloads.py      # NEW: PDF download functionality test
├── download_server.py         # NEW: Alternative download server
├── requirements.txt            # Python dependencies
├── README.md                  # This documentation
├── BATCH_README.md            # NEW: Detailed batch processing guide
├── TROUBLESHOOTING_DOWNLOADS.md  # NEW: Download troubleshooting guide
├── test_installation.py       # Installation verification
├── demo.py                    # Individual processing demo
├── example_usage.py           # Programmatic usage examples
├── config.ini                 # Advanced configuration options
└── .gitignore                 # Git ignore file
```

## Quick Start

### Individual Check Processing
The easiest way to process single checks is through the web interface:

```bash
python start_check_resizer.py
```

This opens a web browser with an intuitive interface where you can:
- Upload check images by drag-and-drop or clicking to browse
- Preview results before downloading
- Download cropped images with one click
- See detailed processing statistics

### 🆕 Batch Check Processing (NEW!)
For processing multiple checks with automatic classification and print layouts:

```bash
python start_batch_processor.py
```

This opens a specialized batch interface where you can:
- **Upload multiple checks** at once (drag-and-drop supported)
- **Automatic classification** into Personal, Business, and Commercial types
- **Generate print-ready PDFs** with 3 checks per page, grouped by type
- **Download organized results** as individual PDFs or complete ZIP file
- **View detailed reports** with processing statistics and confidence scores

## Usage

### Web UI (Recommended for most users)

#### Individual Check Processing
```bash
# Start the individual processing UI
python start_check_resizer.py

# Or directly with streamlit  
python -m streamlit run ui.py
```

#### Batch Processing (NEW!)
```bash
# Start the batch processing UI
python start_batch_processor.py

# Or directly with streamlit (uses port 8502)
python -m streamlit run batch_ui.py --server.port 8502
```

### Command Line Interface

#### Process a single image:
```bash
python check_resizer.py input_check.jpg
python check_resizer.py input_check.jpg -o output_check.jpg

# With background leveling (enabled by default)
python check_resizer.py input_check.jpg --level-method gaussian

# Disable auto-rotation
python check_resizer.py input_check.jpg --no-auto-rotate

# Disable background leveling
python check_resizer.py input_check.jpg --no-level-background
```

#### Process with preview:
```bash
python check_resizer.py input_check.jpg --preview
```

#### Batch process all images in a directory:
```bash
python check_resizer.py input_folder/ --batch

# With specific leveling method
python check_resizer.py input_folder/ --batch --level-method polynomial
```

#### 🆕 Advanced Batch Processing with Classification:
```bash
# Process multiple checks and create print-ready PDFs
python demo_batch.py  # Creates sample data and demonstrates workflow

# Programmatic batch processing
python -c "
from check_batch_processor import CheckBatchProcessor
processor = CheckBatchProcessor()
results = processor.process_batch(['check1.jpg', 'check2.png'], './output/')
print(f'Generated {len(results[\"pdf_files\"])} PDF files')
"
```

### 🆕 Batch Processing Features

The new batch processing system provides enterprise-level features:

#### Automatic Check Classification
- **Personal Checks**: ~6" × 2.75" (standard personal banking)
- **Business Checks**: ~8.5" × 3.5" (business payments)  
- **Commercial Checks**: ~8.5" × 11" (voucher-style with stubs)

#### Print Layout Generation
- **Smart Grouping**: Automatically groups checks by type
- **Professional PDFs**: 3 checks per page with proper margins
- **Scalable Output**: Maintains aspect ratios and print quality
- **Metadata**: Includes filenames, page numbers, and timestamps

#### Configuration Options
```python
from check_batch_processor import CheckBatchProcessor

processor = CheckBatchProcessor()

# Customize print layout
processor.print_settings['checks_per_page'] = 4  # 1-4 checks per page
processor.print_settings['margin'] = 0.75       # Custom margins
processor.print_settings['page_size'] = A4      # Different page size

# Process with custom settings
results = processor.process_batch(image_paths, output_dir)
```

### Programmatic Usage

#### Individual Processing
```python
from check_resizer import CheckResizer

# Initialize the resizer
resizer = CheckResizer()

# Process a single image with background leveling
resizer.resize_image('check.jpg', 'cropped_check.jpg', 
                    preview=True, level_background=True, level_method='morphological')

# Batch process a directory without leveling
resizer.batch_resize('input_directory/', 'output_directory/', 
                    level_background=False)
```

#### 🆕 Batch Processing with Classification
```python
from check_batch_processor import CheckBatchProcessor

processor = CheckBatchProcessor()

# Process multiple checks with automatic classification
results = processor.process_batch([
    'personal_check1.jpg',
    'business_check.png', 
    'commercial_check.pdf'
], output_dir='./processed_checks/')

# Access results
print(f"Processed {len(results['processed_checks'])} checks")
print(f"Classification: {results['classification_summary']}")
print(f"Generated PDFs: {len(results['pdf_files'])}")

# Download individual PDFs
for pdf_info in results['pdf_files']:
    print(f"{pdf_info['type']}: {pdf_info['path']} ({pdf_info['check_count']} checks)")
```

## 🔧 Alternative Download Methods

If you experience issues downloading PDFs from the web interface:

### Simple File Server
Start a basic file server for direct downloads:
```bash
# Serve demo output files
python download_server.py --directory demo_batch_output

# Serve custom directory
python download_server.py --directory /path/to/your/output

# Use different port if needed
python download_server.py --port 8504
```

This opens `http://localhost:8503` with clickable download links.

### Manual File Access
Processed files are saved in these locations:
- **Demo output**: `./demo_batch_output/`
- **Test output**: `./test_batch_output/`
- **Custom processing**: Specify your own output directory

### Verify Downloads Work
Test the download functionality:
```bash
python test_pdf_downloads.py
```

## How It Works

The tool uses computer vision techniques to analyze check images:

1. **Background Leveling** (optional, enabled by default): Removes background variations, shadows, and uneven lighting
   - **Morphological**: Uses mathematical morphology to separate content from background (best for most documents)
   - **Gaussian**: Uses large Gaussian blur for background estimation (fast, good for simple backgrounds)  
   - **Polynomial**: Fits polynomial surfaces to model complex lighting variations (advanced, handles gradients)

2. **Preprocessing**: Converts images to grayscale, applies Gaussian blur, and enhances contrast
2. **Edge Detection**: Uses multiple algorithms:
   - Canny edge detection for sharp boundaries
   - Adaptive thresholding for varying lighting conditions
   - Morphological operations for noise reduction
   - Edge density analysis for advanced detection
   - Brightness analysis as fallback method
3. **Boundary Analysis**: Finds the largest content area (the check)
4. **Smart Cropping**: Adds appropriate padding to ensure no content is lost
5. **Quality Preservation**: Uses PIL for final image processing to maintain quality

## Supported Formats

- Input: JPG, JPEG, PNG, BMP, TIFF, TIF
- Output: Same as input format (or specify different format by extension)

## Command Line Options

```
usage: check_resizer.py [-h] [-o OUTPUT] [-p] [-b] [--level-background] [--no-level-background] [--level-method {morphological,gaussian,polynomial}] input

positional arguments:
  input                 Input image file or directory

options:
  -h, --help           show this help message and exit
  -o OUTPUT, --output OUTPUT
                       Output file or directory
  -p, --preview        Show preview of cropped images
  -b, --batch          Process all images in input directory
  --level-background   Apply background leveling (default: enabled)
  --no-level-background
                       Disable background leveling
  --level-method {morphological,gaussian,polynomial}
                       Background leveling method (default: morphological)
```

## Examples

### Example 1: Single Image Processing
```bash
# Basic processing
python check_resizer.py my_check.jpg

# With custom output name
python check_resizer.py my_check.jpg -o processed_check.jpg

# With preview window
python check_resizer.py my_check.jpg --preview
```

### Example 2: Batch Processing
```bash
# Process all images in 'scanned_checks' folder
python check_resizer.py scanned_checks/ --batch

# Save to specific output directory
python check_resizer.py scanned_checks/ --batch -o processed_checks/

# Preview first few images (useful for testing)
python check_resizer.py scanned_checks/ --batch --preview
```

### Example 3: Web UI Usage
```bash
# Launch the web interface
python launch_ui.py

# The interface will open in your browser at http://localhost:8501
# 1. Upload a check image using the file uploader
# 2. Wait for automatic processing
# 3. Review the before/after comparison
# 4. Download the cropped result
```

### Example 4: Programmatic Usage
```python
from check_resizer import CheckResizer
from pathlib import Path

resizer = CheckResizer()

# Process all PNG files in a directory
input_dir = Path("raw_scans")
output_dir = Path("cropped_checks")
output_dir.mkdir(exist_ok=True)

for png_file in input_dir.glob("*.png"):
    output_file = output_dir / f"cropped_{png_file.name}"
    resizer.resize_image(png_file, output_file)
```

## Algorithm Details

The tool employs three main computer vision techniques:

### 1. Canny Edge Detection
- Detects sharp edges in the image
- Good for high-contrast check boundaries
- Uses Gaussian blur preprocessing to reduce noise

### 2. Adaptive Thresholding
- Handles varying lighting conditions
- Uses local pixel neighborhoods for thresholding
- Effective for checks with uneven illumination

### 3. Morphological Operations
- Uses mathematical morphology to analyze shapes
- Effective at closing small gaps and removing noise
- Good for degraded or low-quality images

The tool automatically selects the best result based on:
- Area reduction percentage (optimal range: 10-80%)
- Boundary validity checks
- Content preservation criteria

## Troubleshooting

If you encounter the error "❌ Could not determine crop boundaries", see the detailed [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide.

### Quick Solutions:

1. **Use Manual Cropping**: In the web UI, enable manual cropping mode
2. **Improve Image Quality**: Ensure good contrast and lighting
3. **Try Different Formats**: Convert to PNG if using JPEG
4. **Add Debug Info**: Use the debug checkbox in the web UI

For detailed troubleshooting steps, error explanations, and advanced solutions, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Common Issues

1. **"Could not load image" error**
   - Check file path is correct
   - Ensure image format is supported
   - Verify file is not corrupted

2. **"No valid bounds found" message**
   - Image may have very low contrast
   - Check might fill entire image (no whitespace to remove)
   - Try preprocessing the image manually

3. **Poor cropping results**
   - Use `--preview` flag to see results before saving
   - Check may have unusual layout or poor scan quality
   - Consider manual preprocessing

### Performance Tips

- For batch processing, disable preview unless needed
- Larger images take longer to process
- TIFF files may require more memory

## Dependencies

- OpenCV (cv2): Computer vision and image processing
- NumPy: Numerical computations
- Pillow (PIL): High-quality image I/O and manipulation
- Matplotlib: Preview visualization (optional)

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the tool.

## License

This project is open source. Please check the license file for details.