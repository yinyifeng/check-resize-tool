# Troubleshooting Guide - Check Batch Processor

## PDF Download Issues

If you're experiencing problems downloading PDFs from the batch processor, try these solutions:

### 1. Browser Issues
- **Refresh the page** and try processing again
- **Clear browser cache** and cookies
- **Try a different browser** (Chrome, Firefox, Safari)
- **Disable browser extensions** that might block downloads
- **Check download folder permissions**

### 2. Session Issues
- **Don't navigate away** from the results page after processing
- **Avoid refreshing** the page after processing completes
- If you see "File not found" errors, **process the batch again**

### 3. File Size Issues
- Large batches may create big PDF files
- Check your **available disk space**
- Consider processing **smaller batches** (5-10 files at a time)

### 4. Network Issues
- Ensure **stable internet connection**
- **Disable VPN** if using one
- Try **downloading one file at a time** instead of ZIP

### 5. Common Error Messages

#### "File not found"
**Problem**: PDF file path is incorrect
**Solution**: 
1. Process the batch again
2. Don't refresh the page after processing
3. Try downloading immediately after processing completes

#### "Error reading file"
**Problem**: File permissions or corruption
**Solution**:
1. Check available disk space
2. Restart the application: `python start_batch_processor.py`
3. Process a smaller batch

#### "ZIP creation failed"
**Problem**: Temporary directory cleanup
**Solution**:
1. Download individual PDFs instead
2. Restart the application
3. Clear browser cache

### 6. Testing Download Functionality

Run the test script to verify everything is working:
```bash
python test_pdf_downloads.py
```

This will create sample files and test the complete download workflow.

### 7. Manual File Access

If downloads still fail, you can find processed files in:
- **Demo output**: `./demo_batch_output/` (from demo runs)
- **Test output**: `./test_batch_output/` (from test script)
- **Temporary files**: Usually in `/tmp/` or system temp directory

### 8. Alternative Solutions

#### Command Line Processing
If the web interface has persistent issues:
```bash
# Create sample data and process
python demo_batch.py

# Check the output folder
ls demo_batch_output/
```

#### Direct API Usage
```python
from check_batch_processor import CheckBatchProcessor

processor = CheckBatchProcessor()
results = processor.process_batch(['file1.jpg', 'file2.png'], './output')

# PDFs will be in ./output/ folder
```

### 9. Getting Help

If issues persist:

1. **Check the console** for error messages (F12 in browser → Console tab)
2. **Run the test script** to verify functionality
3. **Try the demo** to confirm the system works: `python demo_batch.py`
4. **Check file permissions** in your output directory
5. **Restart the application** completely

### 10. Known Limitations

- **Session Storage**: Files are stored in temporary directories and may be cleaned up
- **Large Files**: Very large images may cause memory issues
- **Concurrent Users**: Multiple users may conflict with temporary file storage
- **Browser Limits**: Some browsers limit download sizes or concurrent downloads

## Quick Fix Checklist

- [ ] Page not refreshed after processing
- [ ] Browser allows downloads from localhost
- [ ] Sufficient disk space available  
- [ ] No browser extensions blocking downloads
- [ ] Stable internet connection
- [ ] Files processed successfully (no errors in processing)
- [ ] Tried downloading immediately after processing
- [ ] Test script passes: `python test_pdf_downloads.py`

If all items are checked and downloads still fail, restart the application and process a smaller batch.