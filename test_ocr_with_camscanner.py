#!/usr/bin/env python3
"""
Test OCR with CamScanner images
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.utils import extract_text_from_image, validate_image_file
from django.core.files.uploadedfile import SimpleUploadedFile

def test_camscanner_ocr():
    print("=== TESTING CAMSCANNER OCR ===\n")
    
    # Test with a sample image path (you'll need to provide this)
    image_path = input("Enter the path to your CamScanner image: ").strip()
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return
    
    print(f"✅ Image found: {image_path}")
    print(f"✅ File size: {os.path.getsize(image_path)} bytes")
    
    # Read the image file
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # Create a SimpleUploadedFile
    image_file = SimpleUploadedFile(
        "camscanner_test.jpg",
        image_data,
        content_type="image/jpeg"
    )
    
    print(f"✅ Created upload file: {image_file.name}")
    print(f"✅ File size: {image_file.size} bytes")
    
    # Test image validation
    print("\n=== TESTING IMAGE VALIDATION ===")
    is_valid, error_msg = validate_image_file(image_file)
    print(f"Validation result: {is_valid}")
    if not is_valid:
        print(f"Error: {error_msg}")
        return
    
    # Test OCR extraction
    print("\n=== TESTING OCR EXTRACTION ===")
    ocr_text, ocr_error = extract_text_from_image(image_file)
    
    if ocr_text:
        print(f"✅ OCR Success!")
        print(f"Extracted text: '{ocr_text}'")
        print(f"Text length: {len(ocr_text)} characters")
    else:
        print(f"❌ OCR Failed!")
        print(f"Error: {ocr_error}")
    
    # Test with different OCR configurations
    print("\n=== TESTING DIFFERENT OCR CONFIGS ===")
    
    import pytesseract
    from PIL import Image
    import io
    
    # Reset file pointer
    image_file.seek(0)
    
    # Try different PSM modes
    psm_modes = [6, 8, 13]  # Different page segmentation modes
    
    for psm in psm_modes:
        try:
            image_file.seek(0)
            pil_image = Image.open(image_file)
            
            config = f'--psm {psm}'
            text = pytesseract.image_to_string(pil_image, config=config)
            
            print(f"PSM {psm}: '{text.strip()}'")
            
        except Exception as e:
            print(f"PSM {psm}: Error - {e}")

if __name__ == "__main__":
    test_camscanner_ocr() 