#!/bin/bash
"""
Setup script for Check Resizer on target machine
"""

echo "🔧 Setting up Check Resizer Web Application..."
echo "=============================================="

# Check Python version
python3 --version || {
    echo "❌ Python 3 not found. Please install Python 3.8 or later."
    exit 1
}

echo "✅ Python found"

# Install dependencies
echo "📦 Installing dependencies..."
python3 -m pip install --user -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🎉 Setup complete!"
    echo "=============================================="
    echo "To start Check Resizer:"
    echo "  python3 start_check_resizer.py"
    echo ""
    echo "Or on Windows:"
    echo "  python start_check_resizer.py"
    echo ""
    echo "The web interface will open at: http://localhost:8501"
else
    echo "❌ Failed to install dependencies"
    echo "Try running manually:"
    echo "  pip install streamlit opencv-python pillow numpy scipy scikit-learn matplotlib"
    exit 1
fi