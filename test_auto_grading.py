#!/usr/bin/env python3
"""
Test auto-grading for existing student answers
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.contrib.auth.models import User
from student.models import SubjectiveAnswer, StuExam_DB
from student.utils import grade_answer, get_reference_answers_for_question

def test_auto_grading():
    print("🧪 TESTING AUTO-GRADING SYSTEM")
    print("=" * 40)
    
    # Get all ungraded student answers
    ungraded_answers = SubjectiveAnswer.objects.filter(marks=0) # type: ignore
    print(f"Found {ungraded_answers.count()} ungraded answers")
    
    if ungraded_answers.count() == 0:
        print("✅ All answers are already graded!")
        return
    
    graded_count = 0
    no_reference_count = 0
    
    for answer in ungraded_answers:
        print(f"\n--- Testing Answer {answer.id} ---")
        print(f"Student: {answer.student.username}")
        print(f"Question: {answer.question.question[:50]}...")
        print(f"Answer content: {answer.text_answer or answer.ocr_text or 'No content'}")
        
        # Check if reference answers exist
        reference_answers = get_reference_answers_for_question(answer.question)
        
        if reference_answers.count() == 0: # type: ignore
            print("❌ No reference answers found - cannot grade")
            no_reference_count += 1
        else:
            print(f"✅ Found {reference_answers.count()} reference answer(s)") # type: ignore
            
            # Try to grade
            try:
                score, feedback, best_reference = grade_answer(answer, reference_answers)
                
                # Update the answer
                answer.marks = score
                answer.feedback = feedback
                answer.save()
                
                print(f"✅ Graded: {score}/5 marks")
                print(f"   Feedback: {feedback}")
                graded_count += 1
                
            except Exception as e:
                print(f"❌ Grading failed: {e}")
    
    print(f"\n📊 GRADING SUMMARY:")
    print(f"   - Successfully graded: {graded_count}")
    print(f"   - No reference answers: {no_reference_count}")
    print(f"   - Total processed: {graded_count + no_reference_count}")
    
    if no_reference_count > 0:
        print(f"\n💡 To enable auto-grading for remaining answers:")
        print(f"   Create reference answers for {no_reference_count} questions in Django admin")

if __name__ == "__main__":
    test_auto_grading() 