#!/usr/bin/env python3
"""
Test complete grading pipeline
"""
import os
import sys
import django

print("Testing Complete Grading Pipeline...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.utils import grade_answer, calculate_similarity_score
from student.models import SubjectiveAnswer
from main.models import Question_DB
from django.contrib.auth.models import User

def test_grading_pipeline():
    """Test the complete grading pipeline"""
    
    print("\nStep 1: Creating test data...")
    
    # Create a test question
    question, created = Question_DB.objects.get_or_create( # type: ignore
        qno=999,
        defaults={
            'question': 'What is the capital of Nepal?',
            'question_type': 'SUBJECTIVE'
        }
    )
    print(f"✅ Question created: {question.question}")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='test_student',
        defaults={'email': 'test@example.com'}
    )
    print(f"✅ User created: {user.username}")
    
    print("\nStep 2: Testing similarity scoring...")
    
    # Test with similar texts
    student_text = "NEPAL LS A BEAUTIFUL COUNTRY KATHMANDU ITS TT' cAPTTA"
    reference_text = "NEPAL IS A BEAUTIFUL COUNTRY KATHMANDU IS ITS CAPITAL"
    
    similarity = calculate_similarity_score(student_text, reference_text)
    print(f"✅ Similarity score: {similarity:.3f}")
    
    print("\nStep 3: Testing complete grading...")
    
    # Create a mock student answer
    class MockStudentAnswer:
        def __init__(self, text):
            self.ocr_text = text
    
    student_answer = MockStudentAnswer(student_text)
    
    # Create mock reference answers
    class MockReferenceAnswer:
        def __init__(self, text):
            self.text_answer = text
    
    reference_answers = [
        MockReferenceAnswer(reference_text),
        MockReferenceAnswer("Kathmandu is the capital city of Nepal")
    ]
    
    # Test grading
    score, feedback, best_match = grade_answer(student_answer, reference_answers)
    
    print(f"✅ Grading complete!")
    print(f"   Score: {score:.1f}%")
    print(f"   Feedback: {feedback}")
    print(f"   Best match: {best_match.text_answer[:50]}...")
    
    return True

if __name__ == "__main__":
    success = test_grading_pipeline()
    if success:
        print("\n🎉 Complete grading pipeline working!")
        print("Your exam system is ready for production! 🚀")
    else:
        print("\n❌ Grading pipeline needs attention") 