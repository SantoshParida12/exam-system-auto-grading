#!/usr/bin/env python3
"""
Test script to simulate student submitting an answer
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.models import SubjectiveAnswer, StuExam_DB
from main.models import Question_DB
from django.contrib.auth.models import User

def test_student_submission():
    print("=== TESTING STUDENT SUBMISSION ===\n")
    
    # Get the first student and question
    student = User.objects.filter(groups__name="Student").first()
    if not student:
        print("❌ No student found!")
        return
    
    question = Question_DB.objects.first() # type: ignore
    if not question:
        print("❌ No question found!")
        return
    
    print(f"✅ Using student: {student.username}")
    print(f"✅ Using question: {question.question[:50]}...")
    
    # Create a test SubjectiveAnswer
    try:
        subj_answer, created = SubjectiveAnswer.objects.get_or_create( # type: ignore
            question=question,
            student=student,
            defaults={
                'text_answer': 'This is a test answer submitted by the student.',
                'marks': 3,
                'feedback': 'Good answer with room for improvement.'
            }
        )
        
        if created:
            print("✅ Created new SubjectiveAnswer")
        else:
            print("✅ Updated existing SubjectiveAnswer")
            subj_answer.text_answer = 'This is a test answer submitted by the student.'
            subj_answer.marks = 3
            subj_answer.feedback = 'Good answer with room for improvement.'
            subj_answer.save()
        
        print(f"✅ Answer ID: {subj_answer.id}")
        print(f"✅ Text Answer: {subj_answer.text_answer}")
        print(f"✅ Marks: {subj_answer.marks}")
        print(f"✅ Feedback: {subj_answer.feedback}")
        
    except Exception as e:
        print(f"❌ Error creating SubjectiveAnswer: {e}")
        return
    
    # Now test if professor can find it
    print("\n=== TESTING PROFESSOR VIEW ===")
    
    # Simulate the professor's query
    found_answer = SubjectiveAnswer.objects.filter(  # type: ignore
        question=question,
        student=student
    ).first()
    
    if found_answer:
        print("✅ Professor can find the answer!")
        print(f"✅ Answer content: {found_answer.text_answer}")
        print(f"✅ Marks: {found_answer.marks}")
    else:
        print("❌ Professor cannot find the answer!")
    
    # Check total answers
    total_answers = SubjectiveAnswer.objects.count() # type: ignore
    print(f"\n✅ Total SubjectiveAnswer records: {total_answers}")

if __name__ == "__main__":
    test_student_submission() 