#!/usr/bin/env python3
"""
Test script to verify OCR functionality
"""
import os
import sys
import django
import traceback

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.utils import extract_text_from_image
from django.core.files.uploadedfile import SimpleUploadedFile

def test_ocr():
    """Test OCR functionality"""
    print("Testing OCR functionality...")
    
    # Create a simple test image with text
    from PIL import Image, ImageDraw, ImageFont
    import io
    import PIL
    print("Imports successful.")
    print("PIL version:", PIL.__version__)
    
    try:
        # Create a larger test image with text
        img = Image.new('RGB', (800, 200), (255, 255, 255)) # type: ignore
        print("Image created.")
        draw = ImageDraw.Draw(img)
        print("ImageDraw object created.")
        
        # Use default font to avoid issues
        font = ImageFont.load_default()
        print("Using default font")
        print("Font object:", font)
        
        print("About to draw text on image...")
        try:
            # Draw simple, large text
            draw.text((100, 80), "HELLO", fill='black', font=font)
            print("Text drawn on image.")
        except Exception as draw_err:
            print(f"Exception during draw.text: {draw_err}")
            traceback.print_exc()
            return False
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        print("Image saved to bytes.")
        
        # Create a SimpleUploadedFile
        test_file = SimpleUploadedFile(
            "test_image.png",
            img_byte_arr.getvalue(),
            content_type="image/png"
        )
        print("SimpleUploadedFile created.")
        
        print("Created test image with text: 'HELLO'")
        
        # Test OCR extraction
        print("Calling extract_text_from_image...")
        text, error = extract_text_from_image(test_file)
        print("extract_text_from_image returned.")
        
        if error:
            print(f"OCR Error: {error}")
            return False
        
        if text:
            print(f"OCR Success! Extracted text: '{text}'")
            return True
        else:
            print("OCR returned empty text")
            return False
    except Exception as e:
        print(f"OCR Exception: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_ocr()
        if success:
            print("\n✅ OCR test PASSED!")
        else:
            print("\n❌ OCR test FAILED!")
    except Exception as main_e:
        print(f"Fatal error in test script: {main_e}")
        traceback.print_exc() 