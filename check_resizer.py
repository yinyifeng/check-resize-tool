#!/usr/bin/env python3
"""
Check Image Resizer Tool

This program analyzes images of checks and automatically crops them to remove
unnecessary whitespace while preserving the check content.

Features:
- Automatic edge detection and cropping
- Multiple algorithm approaches for different image types
- Batch processing support
- Preview functionality before saving
"""

import cv2
import numpy as np
from PIL import Image
import argparse
import os
import sys
from pathlib import Path


class CheckResizer:
    def __init__(self):
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
    
    def level_image_background(self, image, method='morphological', intensity='gentle'):
        """
        Level the background of an image to make it more uniform.
        
        Args:
            image: Input image (PIL or OpenCV format)
            method: 'morphological', 'gaussian', 'polynomial', or 'none'
            intensity: 'gentle', 'medium', or 'strong'
        
        Returns:
            Leveled image
        """
        if method == 'none':
            return image
            
        # Convert PIL to OpenCV if needed
        if hasattr(image, 'mode'):  # PIL Image
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            cv_image = image.copy()
        
        # Convert to grayscale for processing
        if len(cv_image.shape) == 3:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv_image.copy()
        
        if method == 'morphological':
            return self._level_morphological(cv_image, gray, intensity)
        elif method == 'gaussian':
            return self._level_gaussian(cv_image, gray, intensity)
        elif method == 'polynomial':
            return self._level_polynomial(cv_image, gray, intensity)
        else:
            return cv_image
    
    def _level_morphological(self, cv_image, gray, intensity='gentle'):
        """Level background using morphological operations."""
        # Adjust parameters based on intensity
        if intensity == 'gentle':
            kernel_divisor = 40
            min_kernel = 15
        elif intensity == 'medium':
            kernel_divisor = 25
            min_kernel = 21
        else:  # strong
            kernel_divisor = 15
            min_kernel = 31
        
        # Create a large structuring element to capture background
        kernel_size = min(gray.shape) // kernel_divisor
        kernel_size = max(kernel_size, min_kernel)
        kernel_size = kernel_size if kernel_size % 2 == 1 else kernel_size + 1  # Ensure odd
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        # Get background estimation using morphological opening
        background = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        
        # Smooth the background more heavily to avoid artifacts
        smooth_kernel = kernel_size * 2 + 1
        background = cv2.GaussianBlur(background, (smooth_kernel, smooth_kernel), kernel_size // 3)
        
        # More gentle background subtraction
        # Convert to float for better precision
        gray_float = gray.astype(np.float32)
        bg_float = background.astype(np.float32)
        
        # Gentle subtraction with normalization
        difference = gray_float - bg_float
        
        # Normalize to preserve contrast
        mean_diff = np.mean(difference)
        std_diff = np.std(difference)
        
        # Gentle normalization to maintain original character
        if std_diff > 0:
            normalized = (difference - mean_diff) * (np.std(gray_float) / std_diff) + np.mean(gray_float)
        else:
            normalized = gray_float
        
        # Clip to valid range
        leveled = np.clip(normalized, 0, 255).astype(np.uint8)
        
        # Apply to all channels if color image
        if len(cv_image.shape) == 3:
            leveled_color = cv_image.copy()
            for i in range(3):
                channel = cv_image[:,:,i].astype(np.float32)
                bg_channel = cv2.morphologyEx(cv_image[:,:,i], cv2.MORPH_OPEN, kernel)
                bg_channel = cv2.GaussianBlur(bg_channel, (smooth_kernel, smooth_kernel), kernel_size // 3).astype(np.float32)
                
                diff = channel - bg_channel
                mean_diff = np.mean(diff)
                std_diff = np.std(diff)
                
                if std_diff > 0:
                    norm = (diff - mean_diff) * (np.std(channel) / std_diff) + np.mean(channel)
                else:
                    norm = channel
                
                leveled_color[:,:,i] = np.clip(norm, 0, 255).astype(np.uint8)
            return leveled_color
        else:
            return leveled
    
    def _level_gaussian(self, cv_image, gray, intensity='gentle'):
        """Level background using Gaussian blur method."""
        # Adjust parameters based on intensity
        if intensity == 'gentle':
            kernel_divisor = 20
            min_kernel = 31
        elif intensity == 'medium':
            kernel_divisor = 15
            min_kernel = 51
        else:  # strong
            kernel_divisor = 10
            min_kernel = 71
        
        # Create background estimation using large Gaussian blur
        kernel_size = min(gray.shape) // kernel_divisor
        kernel_size = max(kernel_size, min_kernel)
        kernel_size = kernel_size if kernel_size % 2 == 1 else kernel_size + 1  # Ensure odd
        
        background = cv2.GaussianBlur(gray, (kernel_size, kernel_size), kernel_size // 6)
        
        # Gentle background correction
        gray_float = gray.astype(np.float32)
        bg_float = background.astype(np.float32)
        
        # Calculate ratio instead of subtraction for better preservation
        epsilon = 1.0  # Prevent division by zero
        ratio = gray_float / (bg_float + epsilon)
        
        # Normalize ratio to maintain original brightness
        mean_original = np.mean(gray_float)
        leveled = ratio * mean_original
        
        # Gentle contrast enhancement
        leveled = np.clip(leveled, 0, 255).astype(np.uint8)
        
        # Apply to color image if needed
        if len(cv_image.shape) == 3:
            leveled_color = cv_image.copy()
            for i in range(3):
                channel = cv_image[:,:,i].astype(np.float32)
                bg_channel = cv2.GaussianBlur(channel, (kernel_size, kernel_size), kernel_size // 6).astype(np.float32)
                
                ratio = channel / (bg_channel + epsilon)
                mean_orig = np.mean(channel)
                leveled_channel = ratio * mean_orig
                
                leveled_color[:,:,i] = np.clip(leveled_channel, 0, 255).astype(np.uint8)
            return leveled_color
        else:
            return leveled
    
    def _level_polynomial(self, cv_image, gray, intensity='gentle'):
        """Level background using polynomial surface fitting."""
        try:
            from scipy import ndimage
            from sklearn.preprocessing import PolynomialFeatures
            from sklearn.linear_model import LinearRegression
            import warnings
            warnings.filterwarnings('ignore')
        except ImportError:
            print("Warning: scipy and scikit-learn not available, falling back to Gaussian method")
            return self._level_gaussian(cv_image, gray, intensity)
        
        # Adjust parameters based on intensity
        if intensity == 'gentle':
            degree = 2
            sample_step = max(min(gray.shape) // 50, 20)
        elif intensity == 'medium':
            degree = 3
            sample_step = max(min(gray.shape) // 75, 15)
        else:  # strong
            degree = 3
            sample_step = max(min(gray.shape) // 100, 10)
        
        # Create coordinate matrices
        h, w = gray.shape
        y, x = np.mgrid[0:h, 0:w]
        
        # Sample points for faster processing
        y_sample = y[::sample_step, ::sample_step].ravel()
        x_sample = x[::sample_step, ::sample_step].ravel()
        z_sample = gray[::sample_step, ::sample_step].ravel()
        
        # Create polynomial features
        coords = np.column_stack([x_sample, y_sample])
        poly_features = PolynomialFeatures(degree=degree)
        coords_poly = poly_features.fit_transform(coords)
        
        # Fit polynomial surface
        reg = LinearRegression()
        reg.fit(coords_poly, z_sample)
        
        # Predict background for entire image
        coords_full = np.column_stack([x.ravel(), y.ravel()])
        coords_full_poly = poly_features.transform(coords_full)
        background_flat = reg.predict(coords_full_poly)
        background = background_flat.reshape(h, w).astype(np.float32)
        
        # Gentle background correction using ratio method
        gray_float = gray.astype(np.float32)
        epsilon = 1.0
        ratio = gray_float / (background + epsilon)
        
        # Normalize to preserve original characteristics
        mean_original = np.mean(gray_float)
        leveled = ratio * mean_original
        leveled = np.clip(leveled, 0, 255).astype(np.uint8)
        
        # Apply to color image if needed
        if len(cv_image.shape) == 3:
            leveled_color = cv_image.copy()
            for i in range(3):
                channel = cv_image[:,:,i].astype(np.float32)
                z_sample_color = channel[::sample_step, ::sample_step].ravel()
                reg.fit(coords_poly, z_sample_color)
                bg_channel_flat = reg.predict(coords_full_poly)
                bg_channel = bg_channel_flat.reshape(h, w).astype(np.float32)
                
                ratio = channel / (bg_channel + epsilon)
                mean_orig = np.mean(channel)
                leveled_channel = ratio * mean_orig
                
                leveled_color[:,:,i] = np.clip(leveled_channel, 0, 255).astype(np.uint8)
            return leveled_color
        else:
            return leveled
    
    def load_image(self, image_path):
        """Load an image file and return both OpenCV and PIL versions."""
        try:
            # Load with OpenCV for processing
            cv_image = cv2.imread(str(image_path))
            if cv_image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Load with PIL for final output
            pil_image = Image.open(image_path)
            
            return cv_image, pil_image
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None, None
    
    def preprocess_image(self, image):
        """Preprocess image for better edge detection."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(blurred)
        
        return enhanced
    
    def find_check_bounds_canny(self, image):
        """Find check boundaries using Canny edge detection."""
        processed = self.preprocess_image(image)
        
        # Try multiple Canny threshold combinations for robustness
        threshold_pairs = [
            (50, 150),   # Default
            (30, 100),   # Lower thresholds for faint edges
            (100, 200),  # Higher thresholds for noisy images
            (20, 60),    # Very low for poor quality scans
        ]
        
        for low_thresh, high_thresh in threshold_pairs:
            # Apply Canny edge detection
            edges = cv2.Canny(processed, low_thresh, high_thresh, apertureSize=3)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                continue
            
            # Filter contours by area (remove very small ones)
            height, width = image.shape[:2]
            min_area = (width * height) * 0.05  # At least 5% of image
            valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
            
            if not valid_contours:
                continue
            
            # Find the largest valid contour
            largest_contour = max(valid_contours, key=cv2.contourArea)
            contour_area = cv2.contourArea(largest_contour)
            
            # Check if contour is reasonable size (not too small, not entire image)
            total_area = width * height
            if contour_area < total_area * 0.1 or contour_area > total_area * 0.95:
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Validate aspect ratio (checks are typically wider than tall)
            aspect_ratio = w / h
            if aspect_ratio < 0.5 or aspect_ratio > 10:  # Very flexible range
                continue
            
            # Add padding
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(width - x, w + 2 * padding)
            h = min(height - y, h + 2 * padding)
            
            return (x, y, x + w, y + h)
        
        return None
    
    def find_check_bounds_threshold(self, image):
        """Find check boundaries using adaptive thresholding."""
        processed = self.preprocess_image(image)
        
        # Try different adaptive threshold approaches
        approaches = [
            # (max_value, adaptive_method, threshold_type, block_size, C)
            (255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
            (255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 5),
            (255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2),
            (255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10),
        ]
        
        height, width = image.shape[:2]
        
        for max_val, method, thresh_type, block_size, c in approaches:
            try:
                # Apply adaptive threshold
                thresh = cv2.adaptiveThreshold(processed, max_val, method, thresh_type, block_size, c)
                
                # Invert if needed (check should be dark on light background)
                if np.mean(thresh) < 127:
                    thresh = cv2.bitwise_not(thresh)
                
                # Find non-zero pixels (content areas)
                coords = cv2.findNonZero(255 - thresh)
                
                if coords is None:
                    continue
                
                # Get bounding rectangle of all content
                x, y, w, h = cv2.boundingRect(coords)
                
                # Validate bounds
                area = w * h
                total_area = width * height
                
                # Check if the detected area is reasonable
                if area < total_area * 0.1 or area > total_area * 0.95:
                    continue
                
                # Check aspect ratio
                aspect_ratio = w / h
                if aspect_ratio < 0.5 or aspect_ratio > 10:
                    continue
                
                # Add padding
                padding = 15
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(width - x, w + 2 * padding)
                h = min(height - y, h + 2 * padding)
                
                return (x, y, x + w, y + h)
                
            except Exception:
                continue
        
        return None
    
    def find_check_bounds_morphology(self, image):
        """Find check boundaries using morphological operations."""
        processed = self.preprocess_image(image)
        
        # Try different threshold methods
        threshold_methods = [
            (cv2.THRESH_BINARY + cv2.THRESH_OTSU, None),
            (cv2.THRESH_BINARY, 127),
            (cv2.THRESH_BINARY, 100),
            (cv2.THRESH_BINARY, 150),
        ]
        
        height, width = image.shape[:2]
        
        for thresh_type, thresh_value in threshold_methods:
            try:
                # Apply threshold
                if thresh_value is None:
                    _, binary = cv2.threshold(processed, 0, 255, thresh_type)
                else:
                    _, binary = cv2.threshold(processed, thresh_value, 255, thresh_type)
                
                # Try different kernel sizes for morphological operations
                kernel_sizes = [(5, 5), (3, 3), (7, 7), (9, 9)]
                
                for kernel_size in kernel_sizes:
                    # Create morphological kernel
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
                    
                    # Close small gaps
                    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
                    
                    # Find content bounds
                    coords = cv2.findNonZero(255 - closed)
                    
                    if coords is None:
                        continue
                    
                    x, y, w, h = cv2.boundingRect(coords)
                    
                    # Validate bounds
                    area = w * h
                    total_area = width * height
                    
                    if area < total_area * 0.1 or area > total_area * 0.95:
                        continue
                    
                    # Check aspect ratio
                    aspect_ratio = w / h
                    if aspect_ratio < 0.5 or aspect_ratio > 10:
                        continue
                    
                    # Add padding
                    padding = 10
                    x = max(0, x - padding)
                    y = max(0, y - padding)
                    w = min(width - x, w + 2 * padding)
                    h = min(height - y, h + 2 * padding)
                    
                    return (x, y, x + w, y + h)
                    
            except Exception:
                continue
        
        return None
    
    def find_check_bounds_fallback(self, image):
        """Fallback method using simple brightness analysis."""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            height, width = gray.shape
            
            # Find rows and columns with significant content (non-white areas)
            # Calculate mean brightness for each row and column
            row_means = np.mean(gray, axis=1)
            col_means = np.mean(gray, axis=0)
            
            # Find threshold (assume background is lighter than content)
            overall_mean = np.mean(gray)
            threshold = overall_mean * 0.95  # Slightly below average
            
            # Find content boundaries
            content_rows = np.where(row_means < threshold)[0]
            content_cols = np.where(col_means < threshold)[0]
            
            if len(content_rows) == 0 or len(content_cols) == 0:
                # Try with a more lenient threshold
                threshold = overall_mean * 0.90
                content_rows = np.where(row_means < threshold)[0]
                content_cols = np.where(col_means < threshold)[0]
                
                if len(content_rows) == 0 or len(content_cols) == 0:
                    return None
            
            # Get bounding box
            y1, y2 = content_rows[0], content_rows[-1]
            x1, x2 = content_cols[0], content_cols[-1]
            
            # Validate bounds
            area = (x2 - x1) * (y2 - y1)
            total_area = width * height
            
            if area < total_area * 0.1 or area > total_area * 0.95:
                return None
            
            # Add padding
            padding = 20  # More generous padding for fallback
            x1 = max(0, int(x1) - padding)
            y1 = max(0, int(y1) - padding)
            x2 = min(width, int(x2) + padding)
            y2 = min(height, int(y2) + padding)
            
            return (x1, y1, x2, y2)
            
        except Exception:
            return None
    
    def find_check_bounds_edge_density(self, image):
        """Find bounds using edge density analysis."""
        try:
            processed = self.preprocess_image(image)
            height, width = processed.shape
            
            # Apply Sobel edge detection
            sobelx = cv2.Sobel(processed, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(processed, cv2.CV_64F, 0, 1, ksize=3)
            sobel_combined = np.sqrt(sobelx**2 + sobely**2)
            
            # Normalize
            max_val = np.max(sobel_combined)
            if max_val > 0:
                sobel_normalized = (sobel_combined / max_val * 255).astype(np.uint8)
            else:
                # If no edges found, return None
                return None
            
            # Calculate edge density for each row and column
            row_edges = np.sum(sobel_normalized > 50, axis=1)
            col_edges = np.sum(sobel_normalized > 50, axis=0)
            
            # Find regions with high edge density
            edge_threshold_row = np.percentile(row_edges, 75)
            edge_threshold_col = np.percentile(col_edges, 75)
            
            content_rows = np.where(row_edges > edge_threshold_row)[0]
            content_cols = np.where(col_edges > edge_threshold_col)[0]
            
            if len(content_rows) == 0 or len(content_cols) == 0:
                return None
            
            # Get bounds
            y1, y2 = content_rows[0], content_rows[-1]
            x1, x2 = content_cols[0], content_cols[-1]
            
            # Validate and add padding
            area = (x2 - x1) * (y2 - y1)
            total_area = width * height
            
            if area < total_area * 0.1 or area > total_area * 0.95:
                return None
            
            padding = 15
            x1 = max(0, int(x1) - padding)
            y1 = max(0, int(y1) - padding)
            x2 = min(width, int(x2) + padding)
            y2 = min(height, int(y2) + padding)
            
            return (x1, y1, x2, y2)
            
        except Exception:
            return None
    
    def detect_orientation(self, image):
        """
        Detect if an image needs rotation to be horizontal.
        
        Args:
            image: Input image (OpenCV format)
            
        Returns:
            rotation_angle: 0, 90, 180, or 270 degrees needed for correct orientation
        """
        try:
            # Convert to grayscale for analysis
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            height, width = gray.shape
            
            # Quick aspect ratio check first
            aspect_ratio = width / height
            
            # If clearly horizontal (width > height), probably correct
            if aspect_ratio > 1.2:
                return 0
            
            # If clearly vertical (height > width), probably needs 90° rotation
            if aspect_ratio < 0.8:
                # Test both 90 and 270 degree rotations to see which looks more like a check
                rotation_90 = cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)
                rotation_270 = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
                
                # Analyze text/edge orientation using line detection
                score_90 = self._calculate_horizontal_score(rotation_90)
                score_270 = self._calculate_horizontal_score(rotation_270)
                score_original = self._calculate_horizontal_score(gray)
                
                # Return the rotation that gives the best horizontal score
                scores = {0: score_original, 90: score_90, 270: score_270}
                best_rotation = max(scores, key=scores.get)
                return best_rotation
            
            # For ambiguous cases (aspect ratio near 1:1), use line detection
            orientations = [0, 90, 180, 270]
            scores = {}
            
            for angle in orientations:
                if angle == 0:
                    test_image = gray
                elif angle == 90:
                    test_image = cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)
                elif angle == 180:
                    test_image = cv2.rotate(gray, cv2.ROTATE_180)
                else:  # 270
                    test_image = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
                
                scores[angle] = self._calculate_horizontal_score(test_image)
            
            # Return the angle with the highest horizontal score
            best_angle = max(scores, key=scores.get)
            return best_angle
            
        except Exception as e:
            print(f"Warning: Orientation detection failed: {e}")
            return 0
    
    def _calculate_horizontal_score(self, gray_image):
        """
        Calculate a score indicating how 'horizontal' an image appears.
        Higher scores indicate better horizontal orientation for checks.
        """
        try:
            # Apply edge detection
            edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
            
            # Detect lines using Hough transform
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            horizontal_score = 0
            vertical_score = 0
            
            if lines is not None:
                for line in lines:
                    rho, theta = line[0]
                    angle_deg = theta * 180 / np.pi
                    
                    # Count horizontal lines (near 0° or 180°)
                    if angle_deg < 15 or angle_deg > 165:
                        horizontal_score += 1
                    # Count vertical lines (near 90°)
                    elif 75 < angle_deg < 105:
                        vertical_score += 1
            
            # Additional scoring based on text-like features
            # Checks typically have more horizontal text lines than vertical
            
            # Use morphological operations to detect horizontal vs vertical structures
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
            
            horizontal_pixels = np.sum(horizontal_lines > 0)
            vertical_pixels = np.sum(vertical_lines > 0)
            
            # Combine line detection and morphological analysis
            total_score = (horizontal_score * 2 + horizontal_pixels) - (vertical_score + vertical_pixels * 0.5)
            
            return total_score
            
        except Exception:
            return 0
    
    def rotate_image_if_needed(self, image, auto_rotate=True):
        """
        Automatically detect and correct image orientation.
        
        Args:
            image: Input image (OpenCV format)
            auto_rotate: Whether to perform automatic rotation
            
        Returns:
            rotated_image: Image rotated to horizontal orientation
            rotation_applied: Degrees rotated (0, 90, 180, or 270)
        """
        if not auto_rotate:
            return image, 0
            
        try:
            rotation_needed = self.detect_orientation(image)
            
            if rotation_needed == 0:
                return image, 0
            elif rotation_needed == 90:
                rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                return rotated, 90
            elif rotation_needed == 180:
                rotated = cv2.rotate(image, cv2.ROTATE_180)
                return rotated, 180
            elif rotation_needed == 270:
                rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                return rotated, 270
            else:
                return image, 0
                
        except Exception as e:
            print(f"Warning: Auto-rotation failed: {e}")
            return image, 0

    def analyze_image(self, image):
        """Analyze image using multiple methods and return the best bounds."""
        methods = [
            ("Canny Edge Detection", self.find_check_bounds_canny),
            ("Adaptive Threshold", self.find_check_bounds_threshold),
            ("Morphological Operations", self.find_check_bounds_morphology),
            ("Edge Density Analysis", self.find_check_bounds_edge_density),
            ("Brightness Analysis (Fallback)", self.find_check_bounds_fallback),
        ]
        
        results = []
        height, width = image.shape[:2]
        original_area = width * height
        
        for method_name, method_func in methods:
            try:
                bounds = method_func(image)
                if bounds:
                    x1, y1, x2, y2 = bounds
                    area = (x2 - x1) * (y2 - y1)
                    
                    # Calculate area reduction percentage
                    reduction = (original_area - area) / original_area * 100
                    
                    # Validate bounds make sense
                    if (x2 > x1 and y2 > y1 and 
                        area > original_area * 0.05 and  # Not too small (reduced from 0.1)
                        area < original_area * 0.98):    # Some reduction achieved (relaxed from 0.95)
                        
                        results.append({
                            'method': method_name,
                            'bounds': bounds,
                            'area': area,
                            'reduction': reduction
                        })
                        
                        print(f"Method '{method_name}': bounds {bounds}, reduction {reduction:.1f}%")
            except Exception as e:
                print(f"Method {method_name} failed: {e}")
                continue
        
        if not results:
            print("No valid bounds found with any method")
            return None
        
        # Choose the method that gives reasonable reduction but not too aggressive
        # Prefer methods that reduce area by 5-80% (more lenient)
        best_result = None
        for result in results:
            if 5 <= result['reduction'] <= 80:
                if best_result is None or result['reduction'] > best_result['reduction']:
                    best_result = result
        
        # If no method gives reasonable reduction, pick the one with most reduction
        if best_result is None:
            best_result = max(results, key=lambda x: x['reduction'])
        
        print(f"Selected method: {best_result['method']} "
              f"(Area reduction: {best_result['reduction']:.1f}%)")
        
        return best_result['bounds']
    
    def resize_image(self, image_path, output_path=None, preview=False, level_background=False, level_method='morphological', level_intensity='gentle', auto_rotate=True):
        """Resize a single check image by removing whitespace."""
        print(f"Processing: {image_path}")
        
        # Load image
        cv_image, pil_image = self.load_image(image_path)
        if cv_image is None:
            return False
        
        # Auto-rotate image if needed
        if auto_rotate:
            cv_image, rotation_applied = self.rotate_image_if_needed(cv_image, auto_rotate=True)
            if rotation_applied > 0:
                print(f"Auto-rotated image {rotation_applied}° for horizontal orientation")
                
                # Update PIL image to match rotation
                if len(cv_image.shape) == 3:
                    pil_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
                else:
                    pil_image = Image.fromarray(cv_image, mode='L')
        
        # Apply background leveling if requested
        if level_background:
            print(f"Applying {level_intensity} background leveling using {level_method} method...")
            leveled_cv = self.level_image_background(cv_image, method=level_method, intensity=level_intensity)
            
            # Convert back to PIL for final processing
            if len(leveled_cv.shape) == 3:
                leveled_pil = Image.fromarray(cv2.cvtColor(leveled_cv, cv2.COLOR_BGR2RGB))
            else:
                leveled_pil = Image.fromarray(leveled_cv, mode='L')
                
            # Use leveled image for analysis but keep original for final crop
            analysis_image = leveled_cv
            final_image = leveled_pil
        else:
            analysis_image = cv_image
            final_image = pil_image
        
        # Analyze and find optimal crop bounds
        bounds = self.analyze_image(analysis_image)
        
        if bounds is None:
            print("Could not determine crop bounds, skipping.")
            return False
        
        x1, y1, x2, y2 = bounds
        print(f"Crop bounds: ({x1}, {y1}) to ({x2}, {y2})")
        
        # Crop the image using the final image (leveled or original)
        cropped_image = final_image.crop((x1, y1, x2, y2))
        
        # Show preview if requested
        if preview:
            import matplotlib.pyplot as plt
            if level_background:
                fig, axes = plt.subplots(1, 3, figsize=(18, 6))
                
                axes[0].imshow(pil_image)
                axes[0].set_title('Original Image')
                axes[0].axis('off')
                
                axes[1].imshow(final_image)
                axes[1].set_title(f'Leveled ({level_method}, {level_intensity})')
                axes[1].axis('off')
                
                axes[2].imshow(cropped_image)
                axes[2].set_title('Final Cropped Result')
                axes[2].axis('off')
            else:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
                
                ax1.imshow(pil_image)
                ax1.set_title('Original Image')
                ax1.axis('off')
                
                ax2.imshow(cropped_image)
                ax2.set_title('Cropped Image')
                ax2.axis('off')
            
            plt.tight_layout()
            plt.show()
        
        # Save the cropped image
        if output_path:
            cropped_image.save(output_path, quality=95)
            print(f"Saved cropped image to: {output_path}")
        
        return True
    
    def batch_resize(self, input_dir, output_dir=None, preview=False, level_background=False, level_method='morphological', level_intensity='gentle', auto_rotate=True):
        """Process multiple images in a directory."""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            print(f"Input directory does not exist: {input_dir}")
            return
        
        # Create output directory if specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path / "resized"
            output_path.mkdir(exist_ok=True)
        
        # Find all image files
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(input_path.glob(f"*{ext}"))
            image_files.extend(input_path.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"No supported image files found in {input_dir}")
            return
        
        print(f"Found {len(image_files)} image(s) to process")
        if level_background:
            print(f"Background leveling enabled using {level_intensity} {level_method} method")
        if auto_rotate:
            print("Auto-rotation enabled")
        
        success_count = 0
        for image_file in image_files:
            output_file = output_path / f"resized_{image_file.name}"
            
            if self.resize_image(image_file, output_file, 
                               preview=preview and len(image_files) <= 5,
                               level_background=level_background,
                               level_method=level_method,
                               level_intensity=level_intensity,
                               auto_rotate=auto_rotate):
                success_count += 1
        
        print(f"\nProcessed {success_count}/{len(image_files)} images successfully")


def main():
    parser = argparse.ArgumentParser(description="Analyze and resize check images to remove whitespace")
    parser.add_argument("input", help="Input image file or directory")
    parser.add_argument("-o", "--output", help="Output file or directory")
    parser.add_argument("-p", "--preview", action="store_true", 
                       help="Show preview of cropped images")
    parser.add_argument("-b", "--batch", action="store_true",
                       help="Process all images in input directory")
    parser.add_argument("--level-background", action="store_true", default=False,
                       help="Apply background leveling (default: disabled)")
    parser.add_argument("--level-method", choices=["morphological", "gaussian", "polynomial"],
                       default="morphological", help="Background leveling method (default: morphological)")
    parser.add_argument("--level-intensity", choices=["gentle", "medium", "strong"],
                       default="gentle", help="Background leveling intensity (default: gentle)")
    parser.add_argument("--no-auto-rotate", action="store_true", default=False,
                       help="Disable automatic image rotation detection (default: enabled)")
    
    args = parser.parse_args()
    
    resizer = CheckResizer()
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Input path does not exist: {args.input}")
        sys.exit(1)
    
    if args.batch or input_path.is_dir():
        resizer.batch_resize(args.input, args.output, args.preview, 
                           args.level_background, args.level_method, args.level_intensity, 
                           auto_rotate=not args.no_auto_rotate)
    else:
        # Single file processing
        if args.output:
            output_path = args.output
        else:
            # Create output filename
            stem = input_path.stem
            suffix = input_path.suffix
            output_path = input_path.parent / f"{stem}_resized{suffix}"
        
        resizer.resize_image(args.input, output_path, args.preview,
                           args.level_background, args.level_method, args.level_intensity,
                           auto_rotate=not args.no_auto_rotate)


if __name__ == "__main__":
    main()