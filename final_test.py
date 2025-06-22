#!/usr/bin/env python3
"""
Final OCR test - save image and test with Tesseract directly
"""
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import os

# Configure pytesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Create a test image similar to what the Django app would create
img = Image.new('RGB', (800, 200), (255, 255, 255)) # type: ignore
draw = ImageDraw.Draw(img)

# Use default font
font = ImageFont.load_default()

# Draw text
draw.text((100, 80), "HELLO", fill='black', font=font)

# Save image
img.save('final_test.png')
print("Image saved as final_test.png")

# Test with pytesseract
print("Testing with pytesseract...")
text = pytesseract.image_to_string(img, config='--psm 6')
print(f"pytesseract result: '{text.strip()}'")

# Test with command line Tesseract
print("Testing with command line Tesseract...")
os.system(r'"C:\Program Files\Tesseract-OCR\tesseract.exe" final_test.png stdout --psm 6') 