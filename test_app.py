#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the watermark application
"""

import os
import sys
from PIL import Image
import tempfile

def create_test_image():
    """Create a test image for testing"""
    # Create a simple test image
    img = Image.new('RGB', (800, 600), color='lightblue')
    
    # Create test images directory
    test_dir = "test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # Save test image
    test_image_path = os.path.join(test_dir, "test_image.png")
    img.save(test_image_path, "PNG")
    
    # Create a PNG image with transparency for testing
    transparent_img = Image.new('RGBA', (400, 300), (255, 0, 0, 128))  # Semi-transparent red
    transparent_path = os.path.join(test_dir, "test_transparent.png")
    transparent_img.save(transparent_path, "PNG")
    
    print(f"Test images created in: {test_dir}")
    print(f"- {test_image_path}")
    print(f"- {transparent_path}")
    
    return test_dir

def test_import():
    """Test if all required modules can be imported"""
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
        
        from PIL import Image, ImageDraw, ImageFont, ImageTk
        print("✓ PIL/Pillow imported successfully")
        
        import json
        print("✓ json module available")
        
        # Test basic PIL functionality
        test_img = Image.new('RGB', (100, 100), 'white')
        print("✓ PIL image creation works")
        
        # Test font loading
        try:
            from tkinter.font import families
            fonts = families()
            print(f"✓ Found {len(fonts)} system fonts")
        except Exception as e:
            print(f"⚠ Font loading warning: {e}")
            
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Watermark Application Components")
    print("=" * 50)
    
    # Test imports
    if not test_import():
        print("Import test failed!")
        return False
        
    print("\n" + "=" * 50)
    
    # Create test images
    create_test_image()
    
    print("\n" + "=" * 50)
    print("All tests passed! You can now run the application:")
    print("python watermark_app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
