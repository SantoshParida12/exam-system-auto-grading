#!/usr/bin/env python3
"""
Debug the question relationship issue
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.contrib.auth.models import User
from student.models import StuExam_DB, Stu_Question, SubjectiveAnswer
from main.models import Question_DB

def debug_question_relationship():
    print("🔍 Debugging Question Relationship")
    print("=" * 40)
    
    # Find the test exam
    test_exam = StuExam_DB.objects.filter(examname='test').first() # type: ignore
    if not test_exam:
        print("❌ Test exam not found!")
        return
    
    student = test_exam.student
    print(f"✅ Found test exam: {test_exam.examname}")
    print(f"   Student: {student.username}")
    
    # Check each question in the exam
    for stu_question in test_exam.questions.all():
        print(f"\n--- Stu_Question Analysis ---")
        print(f"Stu_Question qno: {stu_question.qno}")
        print(f"Stu_Question text: {stu_question.question}")
        print(f"Stu_Question original_question: {stu_question.original_question}")
        print(f"Stu_Question original_question qno: {stu_question.original_question.qno if stu_question.original_question else 'None'}")
        
        # Try to find the original question directly
        if stu_question.original_question:
            original_question = stu_question.original_question
            print(f"✅ Original question found: {original_question.question}")
            
            # Look for SubjectiveAnswer
            student_answer = SubjectiveAnswer.objects.filter( # type: ignore
                question=original_question,
                student=student
            ).first()
            
            print(f"SubjectiveAnswer found: {student_answer is not None}")
            if student_answer:
                print(f"   Answer ID: {student_answer.id}")
                print(f"   Text: {student_answer.text_answer}")
                print(f"   Marks: {student_answer.marks}")
            else:
                print(f"   ❌ No SubjectiveAnswer found!")
                
                # Let's check all SubjectiveAnswers for this student
                all_answers = SubjectiveAnswer.objects.filter(student=student) # type: ignore
                print(f"   All answers for this student: {all_answers.count()}")
                for answer in all_answers:
                    print(f"     - Answer {answer.id}: Q{answer.question.qno} - {answer.text_answer}")
        else:
            print(f"❌ No original_question set!")
    
    # Also check all questions in the system
    print(f"\n--- All Questions in System ---")
    all_questions = Question_DB.objects.all() # type: ignore
    print(f"Total questions: {all_questions.count()}")
    for q in all_questions:
        print(f"  Q{q.qno}: {q.question[:50]}...")

if __name__ == "__main__":
    debug_question_relationship() 