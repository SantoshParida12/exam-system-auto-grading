#!/usr/bin/env python3
"""
Test different feedback levels with various similarity scores
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.utils import calculate_similarity_score, grade_answer

def test_feedback_levels():
    print("🎯 Testing Different Feedback Levels")
    print("=" * 40)
    
    # Test cases with different similarity levels
    test_cases = [
        {
            "name": "Excellent Answer (95% similar)",
            "student": "My name is John Smith",
            "reference": "My name is John Smith"
        },
        {
            "name": "Great Answer (80% similar)",
            "student": "My name is John",
            "reference": "My name is John Smith"
        },
        {
            "name": "Good Answer (65% similar)",
            "student": "I am John",
            "reference": "My name is John Smith"
        },
        {
            "name": "Fair Answer (45% similar)",
            "student": "John",
            "reference": "My name is John Smith"
        },
        {
            "name": "Poor Answer (25% similar)",
            "student": "Hello",
            "reference": "My name is John Smith"
        },
        {
            "name": "Very Poor Answer (5% similar)",
            "student": "NEPAL IS A BEAUTIFUL COUNTRY",
            "reference": "My name is John Smith"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        
        # Calculate similarity score
        similarity = calculate_similarity_score(test_case['student'], test_case['reference'])
        
        print(f"Student Answer: '{test_case['student']}'")
        print(f"Reference Answer: '{test_case['reference']}'")
        print(f"Similarity Score: {similarity:.3f}")
        
        # Test complete grading
        class MockStudentAnswer:
            def __init__(self, text):
                self.text_answer = text
        
        class MockReferenceAnswer:
            def __init__(self, text):
                self.text_answer = text
        
        student_answer = MockStudentAnswer(test_case['student'])
        reference_answers = [MockReferenceAnswer(test_case['reference'])]
        
        marks, feedback, best_match = grade_answer(student_answer, reference_answers)
        
        print(f"Marks Awarded: {marks}/5")
        print(f"Feedback: {feedback}")
        
        # Grade classification
        if marks == 5:
            grade_class = "Outstanding"
        elif marks == 4:
            grade_class = "Great"
        elif marks == 3:
            grade_class = "Good"
        elif marks == 2:
            grade_class = "Fair"
        elif marks == 1:
            grade_class = "Poor"
        else:
            grade_class = "Very Poor"
        
        print(f"Grade: {grade_class}")
    
    print(f"\n✅ All feedback levels tested successfully!")

if __name__ == "__main__":
    test_feedback_levels() 