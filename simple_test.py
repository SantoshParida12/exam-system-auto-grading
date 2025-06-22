#!/usr/bin/env python3
"""
Simple OCR test
"""
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import os

# Configure pytesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Create a larger image
img = Image.new('RGB', (800, 400), (255, 255, 255)) # type: ignore
draw = ImageDraw.Draw(img)

# Try to use a larger font
try:
    font = ImageFont.truetype("arial.ttf", 72)
    print("Using Arial font")
except:
    font = ImageFont.load_default()
    print("Using default font")

# Draw large, simple text
draw.text((100, 150), "HELLO", fill='black', font=font)

# Save image
img.save('simple_test.png')
print("Image saved as simple_test.png")

# Test OCR with different configurations
configs = [
    '',  # Default
    '--psm 6',  # Assume uniform block of text
    '--psm 8',  # Single word
    '--psm 13',  # Raw line
]

for i, config in enumerate(configs):
    try:
        text = pytesseract.image_to_string(img, config=config)
        print(f"Config {i} ({config}): '{text.strip()}'")
    except Exception as e:
        print(f"Config {i} Error: {e}") 