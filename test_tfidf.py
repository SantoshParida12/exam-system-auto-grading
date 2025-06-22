#!/usr/bin/env python3
"""
Test TF-IDF generation
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.utils import generate_tfidf_vector, preprocess_text_for_tfidf

def test_tfidf():
    """Test TF-IDF generation"""
    print("Testing TF-IDF generation...")
    
    # Test with the OCR text you provided
    test_text = "NEPAL LS A BEAUTIFUL COUNTRY — _ KATHMANDU ITS TT' cAPTTA)- -—:result but"
    print(f"Input text: '{test_text}'")
    
    # Test preprocessing
    processed_text = preprocess_text_for_tfidf(test_text)
    print(f"Preprocessed text: '{processed_text}'")
    
    # Test TF-IDF generation
    tfidf_result = generate_tfidf_vector(test_text)
    
    if tfidf_result:
        print("TF-IDF generation successful!")
        print(f"Vector length: {len(tfidf_result['vector'])}")
        print(f"Feature names count: {len(tfidf_result['feature_names'])}")
        print(f"Sample features: {tfidf_result['feature_names'][:10]}")
        print(f"Sample vector values: {tfidf_result['vector'][:10]}")
        return True
    else:
        print("TF-IDF generation failed!")
        return False

if __name__ == "__main__":
    success = test_tfidf()
    if success:
        print("\n✅ TF-IDF test PASSED!")
    else:
        print("\n❌ TF-IDF test FAILED!") 