#!/usr/bin/env python3
"""
Streamlit Web UI for Check Resizer Tool

A simple web interface for uploading check images and downloading cropped results.
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import base64
from pathlib import Path
import time
import sys
from contextlib import redirect_stdout
from check_resizer import CheckResizer


def setup_page():
    """Configure the Streamlit page."""
    st.set_page_config(
        page_title="Check Resizer Tool",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📋 Check Image Resizer")
    st.markdown("""
    Upload check images to automatically remove whitespace and crop to content.
    The tool uses computer vision to detect check boundaries and preserve all important content.
    """)


def create_download_link(img_bytes, filename):
    """Create a download link for processed images."""
    b64_img = base64.b64encode(img_bytes).decode()
    href = f'<a href="data:image/png;base64,{b64_img}" download="{filename}">📥 Download Cropped Image</a>'
    return href


def process_image_ui(uploaded_file, resizer, level_background=False, level_method='morphological', level_intensity='gentle'):
    """Process uploaded image and display results."""
    try:
        # Convert uploaded file to PIL Image
        pil_image = Image.open(uploaded_file)
        
        # Convert PIL to OpenCV for processing
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Check if manual crop mode is enabled
        if st.session_state.get('manual_crop_mode', False):
            st.subheader("✂️ Manual Cropping")
            st.write("Click and drag to select the area you want to keep:")
            
            # Use streamlit-cropper for manual cropping
            try:
                from streamlit_cropper import st_cropper
                
                # Crop the image manually
                cropped_img = st_cropper(
                    pil_image, 
                    realtime_update=True, 
                    box_color='#FF0000',
                    aspect_ratio=None
                )
                
                if cropped_img is not None:
                    st.subheader("📋 Manual Crop Result")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Original:**")
                        st.image(pil_image, use_column_width=True)
                    
                    with col2:
                        st.write("**Manually Cropped:**")
                        st.image(cropped_img, use_column_width=True)
                    
                    # Calculate statistics
                    original_area = pil_image.size[0] * pil_image.size[1]
                    cropped_area = cropped_img.size[0] * cropped_img.size[1]
                    reduction = (original_area - cropped_area) / original_area * 100
                    
                    st.metric("Area Reduction", f"{reduction:.1f}%")
                    
                    # Download section
                    st.subheader("💾 Download Manually Cropped Image")
                    
                    # Convert to bytes for download
                    img_bytes = io.BytesIO()
                    if uploaded_file.name.lower().endswith(('.jpg', '.jpeg')):
                        cropped_img.save(img_bytes, format='JPEG', quality=95)
                        file_ext = '.jpg'
                    else:
                        cropped_img.save(img_bytes, format='PNG')
                        file_ext = '.png'
                    
                    img_bytes = img_bytes.getvalue()
                    
                    # Create download filename
                    original_name = Path(uploaded_file.name).stem
                    download_filename = f"{original_name}_manual_crop{file_ext}"
                    
                    st.download_button(
                        label="📥 Download Manually Cropped Image",
                        data=img_bytes,
                        file_name=download_filename,
                        mime=f"image/{'jpeg' if file_ext == '.jpg' else 'png'}"
                    )
                    
                    # Options to try automatic again
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Try Automatic Detection Again"):
                            st.session_state.manual_crop_mode = False
                            st.rerun()
                    
                    with col2:
                        if st.button("✅ Continue with Manual Crop"):
                            st.session_state.manual_crop_mode = False
                    
                return True
                
            except ImportError:
                st.error("Manual cropping feature requires streamlit-cropper. Install it with: pip install streamlit-cropper")
                if st.button("🔙 Back to Automatic Detection"):
                    st.session_state.manual_crop_mode = False
                    st.rerun()
                return False
        
        # Show original image info
        st.subheader("📋 Original Image")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(pil_image, caption="Original Check Image", use_column_width=True)
        
        with col2:
            st.write("**Image Information:**")
            st.write(f"- **Filename:** {uploaded_file.name}")
            st.write(f"- **Size:** {pil_image.size[0]} × {pil_image.size[1]} pixels")
            st.write(f"- **Format:** {pil_image.format}")
            st.write(f"- **Mode:** {pil_image.mode}")
            
            # File size
            file_size = len(uploaded_file.getvalue())
            st.write(f"- **File Size:** {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Process the image
        st.subheader("⚙️ Processing Image...")
        
        # Show processing options being used
        st.write(f"**Processing Settings:**")
        st.write(f"- Background leveling: {'✅ Enabled' if level_background else '❌ Disabled'}")
        if level_background:
            st.write(f"- Leveling method: {level_method.title()}")
            st.write(f"- Intensity: {level_intensity.title()}")
        
        # Add debug option
        show_debug = st.checkbox("Show debug information", value=False, help="Display detailed processing information")
        
        with st.spinner("Analyzing image and finding optimal crop boundaries..."):
            # Apply background leveling if requested
            if level_background:
                st.info(f"🎚️ Applying {level_intensity} {level_method} background leveling...")
                leveled_cv = resizer.level_image_background(cv_image, method=level_method, intensity=level_intensity)
                
                # Convert back to PIL for display
                if len(leveled_cv.shape) == 3:
                    leveled_pil = Image.fromarray(cv2.cvtColor(leveled_cv, cv2.COLOR_BGR2RGB))
                else:
                    leveled_pil = Image.fromarray(leveled_cv, mode='L')
                
                # Use leveled image for analysis
                analysis_image = leveled_cv
                display_image = leveled_pil
            else:
                analysis_image = cv_image
                display_image = pil_image
            
            # Find optimal boundaries
            if show_debug:
                st.write("**Debug Information:**")
                debug_container = st.container()
            
            # Capture print output for debug
            if show_debug:
                f = io.StringIO()
                with redirect_stdout(f):
                    bounds = resizer.analyze_image(analysis_image)
                debug_output = f.getvalue()
                with debug_container:
                    if debug_output:
                        st.text(debug_output)
            else:
                bounds = resizer.analyze_image(analysis_image)
            
            if bounds is None:
                st.error("❌ Could not determine crop boundaries.")
                
                # Provide helpful suggestions
                st.write("**Possible solutions:**")
                st.write("1. **Image Quality**: Ensure the image has good contrast and lighting")
                st.write("2. **Check Content**: Make sure the check has clear visible boundaries")
                st.write("3. **File Format**: Try saving the image in a different format (PNG recommended)")
                st.write("4. **Resolution**: Use a higher resolution scan (at least 300 DPI)")
                st.write("5. **Preprocessing**: Try adjusting the image brightness/contrast before uploading")
                
                # Show image analysis
                st.subheader("🔍 Image Analysis")
                gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Grayscale Version:**")
                    st.image(gray_image, caption="Converted to grayscale", use_column_width=True, channels="GRAY")
                
                with col2:
                    st.write("**Image Statistics:**")
                    st.write(f"- Mean brightness: {np.mean(gray_image):.1f}")
                    st.write(f"- Brightness std: {np.std(gray_image):.1f}")
                    st.write(f"- Min brightness: {np.min(gray_image)}")
                    st.write(f"- Max brightness: {np.max(gray_image)}")
                    
                    # Suggest if image is too uniform
                    if np.std(gray_image) < 20:
                        st.warning("⚠️ Low contrast detected - try improving image contrast")
                    
                    if np.mean(gray_image) > 200:
                        st.warning("⚠️ Image appears very bright - check may not be clearly visible")
                
                # Offer manual cropping option
                st.subheader("✂️ Manual Cropping Option")
                st.write("If automatic detection fails, you can manually crop the image:")
                
                if st.button("🔧 Enable Manual Cropping"):
                    st.session_state.manual_crop_mode = True
                    st.rerun()
                
                return False
            
            x1, y1, x2, y2 = bounds
            
            # Calculate statistics
            original_area = pil_image.size[0] * pil_image.size[1]
            cropped_area = (x2 - x1) * (y2 - y1)
            area_reduction = (original_area - cropped_area) / original_area * 100
            
            # Crop the image
            cropped_image = display_image.crop((x1, y1, x2, y2))
        
        # Show processing results
        st.success("✅ Image processed successfully!")
        
        # Display crop information
        st.subheader("📊 Processing Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Original Dimensions", f"{pil_image.size[0]} × {pil_image.size[1]}")
        with col2:
            st.metric("Cropped Dimensions", f"{x2-x1} × {y2-y1}")
        with col3:
            st.metric("Area Reduction", f"{area_reduction:.1f}%")
        
        # Show crop bounds
        st.write(f"**Crop Boundaries:** ({x1}, {y1}) to ({x2}, {y2})")
        
        # Display comparison
        st.subheader("🔍 Processing Steps")
        
        if level_background:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**1. Original Image**")
                st.image(pil_image, caption="Original with background variations", use_container_width=True)
            
            with col2:
                st.write(f"**2. Leveled ({level_method}, {level_intensity})**")
                st.image(display_image, caption="Background leveled", use_container_width=True)
            
            with col3:
                st.write("**3. Final Cropped**")
                st.image(cropped_image, caption="Cropped to content", use_container_width=True)
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Original Image**")
                st.image(pil_image, caption="Original with whitespace", use_container_width=True)
            
            with col2:
                st.write("**Cropped Image**")
                st.image(cropped_image, caption="Cropped to content", use_container_width=True)
        
        # Download section
        st.subheader("💾 Download Results")
        
        # Convert cropped image to bytes for download
        img_bytes = io.BytesIO()
        
        # Determine output format
        if uploaded_file.name.lower().endswith(('.jpg', '.jpeg')):
            cropped_image.save(img_bytes, format='JPEG', quality=95)
            file_ext = '.jpg'
        else:
            cropped_image.save(img_bytes, format='PNG')
            file_ext = '.png'
        
        img_bytes = img_bytes.getvalue()
        
        # Create download filename
        original_name = Path(uploaded_file.name).stem
        download_filename = f"{original_name}_cropped{file_ext}"
        
        # Download button
        st.download_button(
            label="📥 Download Cropped Image",
            data=img_bytes,
            file_name=download_filename,
            mime=f"image/{'jpeg' if file_ext == '.jpg' else 'png'}"
        )
        
        # File size comparison
        cropped_size = len(img_bytes)
        size_reduction = (file_size - cropped_size) / file_size * 100
        
        st.write(f"**File Size Comparison:**")
        st.write(f"- Original: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        st.write(f"- Cropped: {cropped_size:,} bytes ({cropped_size/1024:.1f} KB)")
        st.write(f"- Size Reduction: {size_reduction:.1f}%")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error processing image: {str(e)}")
        return False


def show_processing_options():
    """Show processing options in the sidebar."""
    st.sidebar.header("⚙️ Processing Options")
    
    # Background leveling options
    leveling_section = st.sidebar.expander("🎚️ Background Leveling", expanded=True)
    with leveling_section:
        level_background = st.checkbox(
            "Enable background leveling", 
            value=False,  # Disabled by default
            help="Remove background variations and make the image more uniform"
        )
        
        if level_background:
            level_method = st.selectbox(
                "Leveling method:",
                ["morphological", "gaussian", "polynomial"],
                index=0,
                help="Choose the background leveling algorithm"
            )
            
            level_intensity = st.selectbox(
                "Intensity:",
                ["gentle", "medium", "strong"],
                index=0,
                help="How aggressively to apply leveling"
            )
            
            st.write("**Method descriptions:**")
            st.write("• **Morphological**: Best for most documents")
            st.write("• **Gaussian**: Fast, good for simple backgrounds") 
            st.write("• **Polynomial**: Advanced, handles complex lighting")
            
            st.write("**Intensity levels:**")
            st.write("• **Gentle**: Minimal distortion (recommended)")
            st.write("• **Medium**: Balanced correction")
            st.write("• **Strong**: Maximum background removal")
        else:
            level_method = "morphological"
            level_intensity = "gentle"
    
    # Store in session state
    st.session_state.level_background = level_background
    st.session_state.level_method = level_method if level_background else "morphological"
    st.session_state.level_intensity = level_intensity if level_background else "gentle"
    
    # Algorithm selection
    algorithm_info = st.sidebar.expander("📖 Algorithm Information")
    with algorithm_info:
        st.write("""
        **The tool uses five algorithms:**
        
        • **Canny Edge Detection** - Best for high-contrast boundaries
        • **Adaptive Thresholding** - Handles varying lighting
        • **Morphological Operations** - Good for noisy images
        • **Edge Density Analysis** - Advanced edge detection
        • **Brightness Analysis** - Statistical fallback method
        
        The best algorithm is automatically selected for each image.
        """)
    
    # Tips
    tips = st.sidebar.expander("💡 Tips for Best Results")
    with tips:
        st.write("""
        **For optimal results:**
        
        • **Enable background leveling** for scanned documents
        • Ensure good lighting when scanning
        • Keep the check flat and straight
        • Include some whitespace around the check
        • Use high resolution (at least 300 DPI)
        • Avoid shadows and glare
        """)
    
    # Supported formats
    formats = st.sidebar.expander("📁 Supported Formats")
    with formats:
        st.write("""
        **Input formats:**
        JPG, JPEG, PNG, BMP, TIFF, TIF
        
        **Output formats:**
        Same as input (JPEG/PNG recommended)
        """)
    
    return level_background, level_method, level_intensity


def main():
    """Main Streamlit application."""
    setup_page()
    level_background, level_method, level_intensity = show_processing_options()
    
    # Initialize the resizer
    if 'resizer' not in st.session_state:
        with st.spinner("Initializing Check Resizer..."):
            st.session_state.resizer = CheckResizer()
    
    resizer = st.session_state.resizer
    
    # File upload section
    st.header("📤 Upload Check Image")
    
    uploaded_file = st.file_uploader(
        "Choose a check image file",
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'],
        help="Upload a scanned check image with whitespace to be cropped"
    )
    
    if uploaded_file is not None:
        # Get processing options
        level_bg = st.session_state.get('level_background', False)
        level_meth = st.session_state.get('level_method', 'morphological')
        level_intens = st.session_state.get('level_intensity', 'gentle')
        
        # Process the uploaded image
        process_image_ui(uploaded_file, resizer, level_bg, level_meth, level_intens)
    
    else:
        # Show example/demo section when no file is uploaded
        st.header("🎯 How It Works")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**1. Upload**")
            st.write("📤 Upload your check image with whitespace")
            
        with col2:
            st.write("**2. Process**")
            st.write("⚙️ AI analyzes and finds check boundaries")
            
        with col3:
            st.write("**3. Download**")
            st.write("📥 Download the cropped, optimized image")
        
        st.markdown("---")
        
        # Demo section
        if st.button("🎮 Run Demo with Sample Images"):
            demo_placeholder = st.empty()
            
            with demo_placeholder.container():
                st.info("🎮 Creating and processing sample check images...")
                
                # Import demo functionality
                from demo import create_sample_check
                import tempfile
                import os
                
                # Create a temporary sample check
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    create_sample_check(tmp_file.name, check_size=(500, 200), canvas_size=(800, 600))
                    
                    # Load and process the sample
                    sample_image = Image.open(tmp_file.name)
                    
                    st.write("**Sample Check Image:**")
                    st.image(sample_image, caption="Sample check with whitespace", width=400)
                    
                    # Process it
                    cv_sample = cv2.cvtColor(np.array(sample_image), cv2.COLOR_RGB2BGR)
                    bounds = resizer.analyze_image(cv_sample)
                    
                    if bounds:
                        x1, y1, x2, y2 = bounds
                        cropped_sample = sample_image.crop((x1, y1, x2, y2))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Before (with whitespace):**")
                            st.image(sample_image, caption="Original", width=300)
                        
                        with col2:
                            st.write("**After (cropped):**")
                            st.image(cropped_sample, caption="Cropped", width=300)
                        
                        # Calculate reduction
                        original_area = sample_image.size[0] * sample_image.size[1]
                        cropped_area = (x2 - x1) * (y2 - y1)
                        reduction = (original_area - cropped_area) / original_area * 100
                        
                        st.success(f"✅ Demo completed! Area reduction: {reduction:.1f}%")
                    
                    # Cleanup
                    os.unlink(tmp_file.name)
        
        # Instructions
        st.markdown("---")
        st.header("📋 Instructions")
        
        st.markdown("""
        1. **Upload your check image** using the file uploader above
        2. **Wait for processing** - the tool will automatically detect check boundaries
        3. **Review the results** - see the before/after comparison
        4. **Download the cropped image** - click the download button to save the result
        
        The tool automatically selects the best processing algorithm for your image and preserves
        all important check content while removing unnecessary whitespace.
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888;'>
        Check Resizer Tool v1.0 | Built with Streamlit | 
        <a href='https://github.com/yinyifeng/check-resize-tool'>GitHub</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()