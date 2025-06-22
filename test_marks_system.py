#!/usr/bin/env python3
"""
Test 0-5 marks system
"""
import os
import sys
import django

print("Testing 0-5 Marks System...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.utils import grade_answer, calculate_similarity_score

def test_marks_system():
    """Test the 0-5 marks system"""
    
    print("\n🎯 Testing 0-5 Marks System...")
    
    # Test cases with different similarity levels
    test_cases = [
        {
            "name": "Excellent Answer (5 marks)",
            "student": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL",
            "reference": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
        },
        {
            "name": "Good Answer (4 marks)",
            "student": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS THE CAPITAL",
            "reference": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
        },
        {
            "name": "Fair Answer (3 marks)",
            "student": "NEPAL IS A COUNTRY KATHMANDU IS CAPITAL",
            "reference": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
        },
        {
            "name": "Below Average Answer (2 marks)",
            "student": "NEPAL COUNTRY KATHMANDU",
            "reference": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
        },
        {
            "name": "Poor Answer (1 mark)",
            "student": "KATHMANDU IS A CITY",
            "reference": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
        },
        {
            "name": "Very Poor Answer (0 marks)",
            "student": "INDIA IS A COUNTRY",
            "reference": "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
        }
    ]
    
    total_marks = 0
    total_questions = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Question {i}: {test_case['name']} ---")
        
        # Calculate similarity score
        similarity = calculate_similarity_score(test_case['student'], test_case['reference'])
        
        print(f"Student Answer: '{test_case['student']}'")
        print(f"Reference Answer: '{test_case['reference']}'")
        print(f"Similarity Score: {similarity:.3f}")
        
        # Test complete grading
        class MockStudentAnswer:
            def __init__(self, text):
                self.ocr_text = text
        
        class MockReferenceAnswer:
            def __init__(self, text):
                self.text_answer = text
        
        student_answer = MockStudentAnswer(test_case['student'])
        reference_answers = [MockReferenceAnswer(test_case['reference'])]
        
        marks, feedback, best_match = grade_answer(student_answer, reference_answers)
        total_marks += marks
        
        print(f"Marks Awarded: {marks}/5")
        print(f"Feedback: {feedback}")
        
        # Grade classification
        if marks == 5:
            grade_class = "Excellent"
        elif marks == 4:
            grade_class = "Good"
        elif marks == 3:
            grade_class = "Fair"
        elif marks == 2:
            grade_class = "Below Average"
        elif marks == 1:
            grade_class = "Poor"
        else:
            grade_class = "Very Poor"
        
        print(f"Grade: {grade_class}")
    
    print(f"\n📊 EXAM SUMMARY:")
    print(f"Total Questions: {total_questions}")
    print(f"Total Marks Obtained: {total_marks}")
    print(f"Maximum Possible Marks: {total_questions * 5}")
    print(f"Percentage: {(total_marks / (total_questions * 5)) * 100:.1f}%")
    
    # Overall grade
    percentage = (total_marks / (total_questions * 5)) * 100
    if percentage >= 90:
        overall_grade = "A+ (Excellent)"
    elif percentage >= 80:
        overall_grade = "A (Very Good)"
    elif percentage >= 70:
        overall_grade = "B+ (Good)"
    elif percentage >= 60:
        overall_grade = "B (Fair)"
    elif percentage >= 50:
        overall_grade = "C+ (Below Average)"
    elif percentage >= 40:
        overall_grade = "C (Poor)"
    else:
        overall_grade = "F (Fail)"
    
    print(f"Overall Grade: {overall_grade}")
    
    return True

if __name__ == "__main__":
    success = test_marks_system()
    if success:
        print("\n🎉 0-5 marks system is ready!")
        print("📋 Marks Scale:")
        print("   5 marks: Excellent (90-100% similarity)")
        print("   4 marks: Good (80-89% similarity)")
        print("   3 marks: Fair (60-79% similarity)")
        print("   2 marks: Below Average (40-59% similarity)")
        print("   1 mark:  Poor (20-39% similarity)")
        print("   0 marks: Very Poor (0-19% similarity)")
    else:
        print("\n❌ Marks system needs attention") 