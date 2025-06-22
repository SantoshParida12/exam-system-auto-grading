#!/usr/bin/env python3
"""
Create a simple test image for OCR testing
"""
from PIL import Image, ImageDraw, ImageFont

# Create a larger test image
img = Image.new('RGB', (600, 200), (255, 255, 255)) # type: ignore
draw = ImageDraw.Draw(img)

# Try to use a larger font
try:
    # Try to use a system font with larger size
    font = ImageFont.truetype("arial.ttf", 48)
except:
    # Fallback to default font
    font = ImageFont.load_default()

# Draw some large, clear text
draw.text((50, 50), "HELLO WORLD", fill='black', font=font)
draw.text((50, 120), "OCR TEST", fill='black', font=font)

# Save the image
img.save('test_image.png')
print("Test image saved as test_image.png")
print("Image size: 600x200 pixels") 