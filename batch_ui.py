#!/usr/bin/env python3
"""
Streamlit UI for Check Batch Processing
Upload multiple check images, auto-classify, and generate print-ready PDFs
"""

import streamlit as st
import tempfile
import os
import shutil
from pathlib import Path
import zipfile
from check_batch_processor import CheckBatchProcessor
from PIL import Image
import json

def main():
    st.set_page_config(
        page_title="Check Batch Processor", 
        page_icon="📋", 
        layout="wide"
    )
    
    st.title("📋 Check Batch Processor")
    st.markdown("Upload multiple check images for automatic classification and print layout generation")
    
    # Initialize session state
    if 'processed_results' not in st.session_state:
        st.session_state.processed_results = None
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = None
    
    # Sidebar settings
    st.sidebar.header("⚙️ Processing Settings")
    
    enable_background_leveling = st.sidebar.checkbox(
        "Enable Background Leveling", 
        value=True,
        help="Remove paper background and improve contrast"
    )
    
    level_intensity = st.sidebar.selectbox(
        "Background Leveling Intensity",
        ["gentle", "medium", "strong"],
        index=0,
        help="How aggressively to remove background"
    )
    
    level_method = st.sidebar.selectbox(
        "Leveling Method",
        ["gaussian", "morphological", "polynomial"],
        index=0,
        help="Algorithm for background removal"
    )
    
    checks_per_page = st.sidebar.selectbox(
        "Checks Per Page",
        [1, 2, 3, 4],
        index=2,  # Default to 3
        help="Number of checks to fit per printed page"
    )
    
    # Main upload interface
    st.header("📤 Upload Check Images")
    
    uploaded_files = st.file_uploader(
        "Choose check image files",
        type=['png', 'jpg', 'jpeg', 'tiff', 'bmp'],
        accept_multiple_files=True,
        help="Upload multiple check images for batch processing"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} files uploaded")
        
        # Preview uploaded files
        with st.expander("🔍 Preview Uploaded Files", expanded=False):
            cols = st.columns(min(len(uploaded_files), 4))
            for i, uploaded_file in enumerate(uploaded_files[:4]):  # Show first 4
                with cols[i % 4]:
                    try:
                        image = Image.open(uploaded_file)
                        st.image(image, caption=uploaded_file.name, use_container_width=True)
                    except:
                        st.error(f"Could not preview {uploaded_file.name}")
            
            if len(uploaded_files) > 4:
                st.info(f"... and {len(uploaded_files) - 4} more files")
        
        # Process button
        if st.button("🚀 Process Batch", type="primary"):
            
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                st.session_state.temp_dir = temp_dir
                
                # Save uploaded files
                input_paths = []
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    input_paths.append(file_path)
                
                # Create output directory
                output_dir = os.path.join(temp_dir, "output")
                
                # Process with progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Initialize processor with custom settings
                    processor = CheckBatchProcessor()
                    processor.print_settings['checks_per_page'] = checks_per_page
                    
                    # Override resizer settings
                    processor.resizer.level_background = enable_background_leveling
                    processor.resizer.level_method = level_method
                    processor.resizer.level_intensity = level_intensity
                    
                    status_text.text("🔄 Processing check images...")
                    progress_bar.progress(0.1)
                    
                    # Process the batch
                    results = processor.process_batch(input_paths, output_dir)
                    
                    progress_bar.progress(1.0)
                    status_text.text("✅ Processing complete!")
                    
                    # Store results in session state
                    st.session_state.processed_results = results
                    
                    # Copy results to a persistent temporary directory
                    persistent_temp_dir = tempfile.mkdtemp(prefix="check_batch_")
                    st.session_state.temp_dir = persistent_temp_dir
                    
                    # Copy output files
                    persistent_output_dir = os.path.join(persistent_temp_dir, "output")
                    shutil.copytree(output_dir, persistent_output_dir)
                    
                    # Update PDF paths to point to persistent directory
                    for pdf_info in results['pdf_files']:
                        old_path = pdf_info['path']
                        filename = Path(old_path).name
                        new_path = os.path.join(persistent_output_dir, filename)
                        pdf_info['path'] = new_path
                    
                    # Update session state with corrected paths
                    st.session_state.processed_results = results
                    
                    st.rerun()  # Refresh to show results
                    
                except Exception as e:
                    st.error(f"❌ Error processing batch: {str(e)}")
                    progress_bar.empty()
                    status_text.empty()
    
    # Display results if available
    if st.session_state.processed_results:
        results = st.session_state.processed_results
        
        st.header("📊 Processing Results")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Processed", len(results['processed_checks']))
        with col2:
            st.metric("Errors", len(results['errors']))
        with col3:
            st.metric("PDF Files", len(results['pdf_files']))
        with col4:
            total_checks = sum(results['classification_summary'].values())
            st.metric("Classified", total_checks)
        
        # Classification breakdown
        if results['classification_summary']:
            st.subheader("📈 Check Classification")
            
            # Create a nice chart
            chart_data = results['classification_summary']
            st.bar_chart(chart_data)
            
            # Detailed breakdown
            for check_type, count in chart_data.items():
                percentage = (count / total_checks * 100) if total_checks > 0 else 0
                st.write(f"**{check_type.title()}**: {count} checks ({percentage:.1f}%)")
        
        # PDF Downloads
        if results['pdf_files'] and st.session_state.temp_dir:
            st.subheader("📄 Download Print-Ready PDFs")
            
            # Debug info
            st.caption(f"📁 Temp directory: {st.session_state.temp_dir}")
            
            for pdf_info in results['pdf_files']:
                pdf_path = pdf_info['path']
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{pdf_info['type'].title()} Checks** - {pdf_info['check_count']} checks, {checks_per_page} per page")
                    
                    # Debug info
                    if not os.path.exists(pdf_path):
                        st.error(f"⚠️ File not found: {pdf_path}")
                        # Try to find the file in the temp directory
                        filename = Path(pdf_path).name
                        alt_path = os.path.join(st.session_state.temp_dir, "output", filename)
                        if os.path.exists(alt_path):
                            st.warning(f"Found at alternative path: {alt_path}")
                            pdf_path = alt_path  # Use the alternative path
                            pdf_info['path'] = alt_path  # Update the stored path
                    else:
                        file_size = os.path.getsize(pdf_path) / 1024  # KB
                        st.caption(f"File size: {file_size:.1f} KB | Path: {Path(pdf_path).name}")
                
                with col2:
                    if os.path.exists(pdf_path):
                        try:
                            with open(pdf_path, "rb") as f:
                                pdf_data = f.read()
                            
                            st.download_button(
                                label=f"📥 Download {pdf_info['type'].title()}",
                                data=pdf_data,
                                file_name=Path(pdf_path).name,
                                mime="application/pdf",
                                key=f"download_{pdf_info['type']}_{len(pdf_data)}"  # Unique key with size
                            )
                        except Exception as e:
                            st.error(f"Error reading file: {str(e)}")
                    else:
                        st.error("❌ File not available")
            
            # Download all as ZIP
            if len(results['pdf_files']) > 1:
                st.subheader("📦 Download All Files")
                
                if st.button("📦 Create ZIP Download"):
                    zip_path = create_download_zip(results, st.session_state.temp_dir)
                    if zip_path:
                        with open(zip_path, "rb") as f:
                            zip_data = f.read()
                        
                        st.download_button(
                            label="📥 Download All PDFs + Summary",
                            data=zip_data,
                            file_name="check_batch_results.zip",
                            mime="application/zip"
                        )
        
        # Processing details
        with st.expander("🔍 Processing Details", expanded=False):
            
            # Show individual check results
            st.subheader("Individual Check Results")
            for i, check_info in enumerate(results['processed_checks']):
                classification = check_info['classification']
                
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"**{Path(check_info['original_path']).name}**")
                
                with col2:
                    st.write(f"Type: {classification['type']}")
                
                with col3:
                    confidence = classification['confidence']
                    color = "green" if confidence > 0.8 else "orange" if confidence > 0.5 else "red"
                    st.write(f":{color}[{confidence:.0%}]")
                
                with col4:
                    dims = classification['dimensions']
                    st.write(f"{dims['width_inches']}\" × {dims['height_inches']}\"")
            
            # Show errors if any
            if results['errors']:
                st.subheader("❌ Errors")
                for error in results['errors']:
                    st.error(error)

def create_download_zip(results, temp_dir):
    """Create a ZIP file with all PDFs and summary."""
    try:
        zip_path = os.path.join(temp_dir, "check_batch_results.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add PDF files
            for pdf_info in results['pdf_files']:
                if os.path.exists(pdf_info['path']):
                    zipf.write(pdf_info['path'], Path(pdf_info['path']).name)
            
            # Add summary files
            output_dir = os.path.join(temp_dir, "output")
            summary_json = os.path.join(output_dir, "batch_summary.json")
            summary_txt = os.path.join(output_dir, "batch_summary.txt")
            
            if os.path.exists(summary_json):
                zipf.write(summary_json, "batch_summary.json")
            
            if os.path.exists(summary_txt):
                zipf.write(summary_txt, "batch_summary.txt")
        
        return zip_path
    except Exception as e:
        st.error(f"Error creating ZIP file: {str(e)}")
        return None

if __name__ == "__main__":
    main()