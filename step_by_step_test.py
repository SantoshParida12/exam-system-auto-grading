#!/usr/bin/env python3
"""
Step-by-step test of OCR and TF-IDF system
"""
import os
import sys
import django

print("Step 1: Setting up Django...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()
print("✅ Django setup complete")

print("\nStep 2: Testing imports...")
try:
    from student.utils import extract_text_from_image, generate_tfidf_vector
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("\nStep 3: Testing TF-IDF with sample text...")
sample_text = "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
tfidf_result = generate_tfidf_vector(sample_text)
if tfidf_result:
    print("✅ TF-IDF generation successful")
    print(f"   Vector length: {len(tfidf_result['vector'])}")
else:
    print("❌ TF-IDF generation failed")

print("\nStep 4: Testing OCR with existing image...")
if os.path.exists('simple_test.png'):
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    with open('simple_test.png', 'rb') as f:
        image_content = f.read()
    
    image_file = SimpleUploadedFile(
        "simple_test.png",
        image_content,
        content_type="image/png"
    )
    
    text, error = extract_text_from_image(image_file)
    
    if error:
        print(f"❌ OCR Error: {error}")
    elif text:
        print(f"✅ OCR Success: '{text[:50]}...'")
    else:
        print("❌ OCR returned empty text")
else:
    print("❌ No test image found")

print("\nStep 5: Testing complete grading pipeline...")
if tfidf_result and text:
    print("✅ All components working - ready for exam system!")
else:
    print("❌ Some components need attention")

print("\n🎯 System Status Summary:")
print(f"   - Django Setup: ✅")
print(f"   - Imports: ✅")
print(f"   - TF-IDF: {'✅' if tfidf_result else '❌'}")
print(f"   - OCR: {'✅' if 'text' in locals() and text else '❌'}")
print(f"   - Overall: {'✅ READY' if tfidf_result and 'text' in locals() and text else '❌ NEEDS WORK'}") 