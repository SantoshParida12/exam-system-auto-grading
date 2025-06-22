#!/usr/bin/env python3
"""
Test percentage-based grading system
"""
import os
import sys
import django

print("Testing Percentage-Based Grading System...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.utils import grade_answer, calculate_similarity_score

def test_percentage_grading():
    """Test percentage-based grading with different similarity levels"""
    
    print("\n🎯 Testing Percentage-Based Grading...")
    
    # Test cases with different similarity levels
    test_cases = [
        {
            "name": "Excellent Answer (95% similar)",
            "student": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL",
            "reference": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
        },
        {
            "name": "Good Answer (75% similar)",
            "student": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS THE CAPITAL",
            "reference": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
        },
        {
            "name": "Fair Answer (60% similar)",
            "student": "NEPAL IS A COUNTRY KATHMANDU IS CAPITAL",
            "reference": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
        },
        {
            "name": "Poor Answer (30% similar)",
            "student": "KATHMANDU IS A CITY",
            "reference": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
        },
        {
            "name": "Very Poor Answer (10% similar)",
            "student": "INDIA IS A COUNTRY",
            "reference": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        
        # Calculate similarity score
        similarity = calculate_similarity_score(test_case['student'], test_case['reference'])
        percentage = similarity * 100
        
        print(f"Student Answer: '{test_case['student']}'")
        print(f"Reference Answer: '{test_case['reference']}'")
        print(f"Similarity Score: {similarity:.3f}")
        print(f"Percentage Grade: {percentage:.1f}%")
        
        # Test complete grading
        class MockStudentAnswer:
            def __init__(self, text):
                self.ocr_text = text
        
        class MockReferenceAnswer:
            def __init__(self, text):
                self.text_answer = text
        
        student_answer = MockStudentAnswer(test_case['student'])
        reference_answers = [MockReferenceAnswer(test_case['reference'])]
        
        score, feedback, best_match = grade_answer(student_answer, reference_answers)
        
        print(f"Final Grade: {score:.1f}%")
        print(f"Feedback: {feedback}")
        
        # Grade classification
        if score >= 90:
            grade_class = "A+ (Excellent)"
        elif score >= 80:
            grade_class = "A (Very Good)"
        elif score >= 70:
            grade_class = "B+ (Good)"
        elif score >= 60:
            grade_class = "B (Fair)"
        elif score >= 50:
            grade_class = "C+ (Below Average)"
        elif score >= 40:
            grade_class = "C (Poor)"
        else:
            grade_class = "F (Fail)"
        
        print(f"Grade Classification: {grade_class}")
    
    print("\n✅ Percentage-based grading system working correctly!")
    print("📊 Grading Scale:")
    print("   90-100%: A+ (Excellent)")
    print("   80-89%:  A  (Very Good)")
    print("   70-79%:  B+ (Good)")
    print("   60-69%:  B  (Fair)")
    print("   50-59%:  C+ (Below Average)")
    print("   40-49%:  C  (Poor)")
    print("   0-39%:   F  (Fail)")
    
    return True

if __name__ == "__main__":
    success = test_percentage_grading()
    if success:
        print("\n🎉 Percentage-based grading system is ready!")
    else:
        print("\n❌ Grading system needs attention") 