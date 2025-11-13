# Check Resizer Troubleshooting Guide

This guide helps resolve common issues when using the Check Resizer Tool.

## Common Error Messages

### "❌ Could not determine crop boundaries"

This error occurs when the tool cannot automatically detect where the check content begins and ends.

#### Possible Causes & Solutions:

1. **Low Contrast Image**
   - **Problem**: The check content is too similar in brightness to the background
   - **Solution**: Increase contrast in your scanning software or photo editor
   - **Test**: Check if the image statistics show low standard deviation (<20)

2. **Poor Image Quality**
   - **Problem**: Blurry, low-resolution, or heavily compressed images
   - **Solution**: 
     - Scan at higher resolution (at least 300 DPI)
     - Use PNG format instead of heavily compressed JPEG
     - Ensure the scanner glass is clean

3. **Insufficient Whitespace**
   - **Problem**: Check fills entire image with little background
   - **Solution**: Include some whitespace around the check when scanning
   - **Minimum**: At least 10-20 pixels of background on all sides

4. **Complex Background**
   - **Problem**: Textured paper, patterns, or shadows in background
   - **Solution**: Use a plain white background when scanning
   - **Alternative**: Try manual cropping mode

5. **Very Dark or Very Bright Images**
   - **Problem**: Extreme brightness levels
   - **Solution**: Adjust brightness to mid-range (mean brightness ~127)

#### Troubleshooting Steps:

1. **Check Image Quality**:
   ```bash
   python check_resizer.py your_image.jpg --preview
   ```
   - Look at the image statistics in debug mode
   - Mean brightness should be 80-200
   - Standard deviation should be >20

2. **Try Different Formats**:
   - Convert JPEG to PNG
   - Reduce JPEG compression if possible

3. **Use Manual Cropping**:
   - In the web UI, click "Enable Manual Cropping"
   - Manually select the check area

4. **Preprocess the Image**:
   - Adjust contrast and brightness
   - Remove any background patterns
   - Ensure check is straight/not rotated

## Image Quality Guidelines

### Optimal Image Characteristics:
- **Resolution**: 300+ DPI for scanned documents
- **Format**: PNG or high-quality JPEG
- **Background**: Plain white or light colored
- **Lighting**: Even, without shadows
- **Content**: High contrast text/lines
- **Orientation**: Check should be straight

### Image Statistics (viewable in debug mode):
- **Mean Brightness**: 100-180 (optimal: 120-160)
- **Brightness Std Dev**: >20 (higher is better for contrast)
- **Min/Max Range**: Should span significant range (not clustered)

## Command Line Debugging

### Enable Verbose Output:
```bash
# Single image with preview
python check_resizer.py problematic_image.jpg --preview

# The tool will show which methods work/fail
```

### Test with Sample Images:
```bash
# Generate and test with sample images
python demo.py

# This creates test images and processes them
```

## Web UI Debugging

### Using Debug Mode:
1. Upload your image
2. Check "Show debug information"
3. Review the method attempts and results
4. Look at image statistics

### Manual Cropping Fallback:
1. If automatic detection fails, click "Enable Manual Cropping"
2. Use the interactive cropper to select the check area
3. Download the manually cropped result

## Advanced Solutions

### Preprocessing Images

If you consistently have issues with certain types of images:

1. **Adjust Contrast** (using PIL):
```python
from PIL import Image, ImageEnhance

# Open image
img = Image.open('check.jpg')

# Enhance contrast
enhancer = ImageEnhance.Contrast(img)
enhanced = enhancer.enhance(1.5)  # Increase contrast by 50%

# Save enhanced version
enhanced.save('check_enhanced.jpg')
```

2. **Convert to Grayscale**:
```python
# Sometimes works better with grayscale
gray_img = img.convert('L')
gray_img.save('check_gray.jpg')
```

3. **Resize Large Images**:
```python
# Very large images can cause issues
if img.size[0] > 2000 or img.size[1] > 2000:
    img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
    img.save('check_resized.jpg')
```

### Custom Configuration

Edit `config.ini` to adjust algorithm parameters:

```ini
[processing]
# Try different Canny thresholds
canny_threshold1 = 30  # Lower for faint edges
canny_threshold2 = 100

# Adjust padding
default_padding = 20  # More generous padding

[validation]
# Allow more aggressive or conservative cropping
min_area_percentage = 5   # Allow smaller detected areas
max_area_percentage = 98  # Allow less reduction
```

## Specific Image Types

### Bank Checks
- Usually work well with default settings
- Ensure check number and routing numbers are visible
- Include signature line area

### Personal Checks
- May have decorative backgrounds - use manual cropping
- Often have lower contrast - enhance before processing

### Business Checks
- Usually high contrast and work well
- May be larger - ensure adequate padding

### Old/Vintage Checks
- Often faded - increase contrast significantly
- May need manual cropping due to age-related artifacts

## Still Having Issues?

### Create a Support Package:

1. **Save Debug Output**:
   ```bash
   python check_resizer.py problem_image.jpg > debug_output.txt 2>&1
   ```

2. **Check Image Properties**:
   - File size
   - Dimensions
   - Format
   - Bit depth

3. **Try All Methods Manually** (modify source to test individual algorithms)

4. **Contact Support** with:
   - Original image (if possible to share)
   - Debug output
   - Image properties
   - What type of check it is

### Quick Fixes to Try:

1. **Crop manually first** to remove excessive background
2. **Adjust brightness** to mid-range
3. **Convert to PNG** if using JPEG
4. **Try a different scanner/camera** if possible
5. **Use the manual cropping feature** in the web UI

### Emergency Workaround:

If all else fails, you can manually specify crop bounds:

```python
from check_resizer import CheckResizer
from PIL import Image

resizer = CheckResizer()
image = Image.open('problem_check.jpg')

# Manually specify crop bounds (x1, y1, x2, y2)
manual_bounds = (100, 50, 700, 300)  # Adjust these values
cropped = image.crop(manual_bounds)
cropped.save('manually_cropped_check.jpg')
```

This guide should help resolve most issues you encounter with the Check Resizer Tool.