#!/usr/bin/env python3
"""
Debug the test exam specifically
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.contrib.auth.models import User
from student.models import SubjectiveAnswer, StuExam_DB
from student.utils import get_reference_answers_for_question, grade_answer
from main.models import Question_DB

def debug_test_exam():
    print("🔍 DEBUGGING TEST EXAM")
    print("=" * 30)
    
    # Find the test exam
    test_exam = StuExam_DB.objects.filter(examname='test').first() # type: ignore
    if not test_exam:
        print("❌ Test exam not found!")
        return
    
    print(f"✅ Found test exam: {test_exam.examname}")
    print(f"   Student: {test_exam.student.username}")
    print(f"   Score: {test_exam.score}%")
    print(f"   Questions: {test_exam.questions.count()}")
    
    # Check each question in the test exam
    for stu_question in test_exam.questions.all():
        print(f"\n--- Question Analysis ---")
        print(f"Question: {stu_question.question}")
        print(f"Original question: {stu_question.original_question}")
        
        # Find student answer
        if stu_question.original_question:
            student_answer = SubjectiveAnswer.objects.filter( # type: ignore
                question=stu_question.original_question,
                student=test_exam.student
            ).first()
        else:
            student_answer = None
        
        if student_answer:
            print(f"✅ Found student answer:")
            print(f"   Text: {student_answer.text_answer}")
            print(f"   OCR: {student_answer.ocr_text}")
            print(f"   Current marks: {student_answer.marks}/5")
            print(f"   Current feedback: {student_answer.feedback}")
            
            # Check for reference answers
            if stu_question.original_question:
                reference_answers = get_reference_answers_for_question(stu_question.original_question) # type: ignore
                print(f"   Reference answers found: {reference_answers.count()}") # type: ignore
                
                if reference_answers.count() > 0: # type: ignore
                    print("   ✅ Reference answers exist - attempting to grade...")
                    try:
                        score, feedback, best_ref = grade_answer(student_answer, reference_answers)
                        print(f"   📊 Grading result: {score}/5 marks")
                        print(f"   📝 Feedback: {feedback}")
                        
                        # Update the answer
                        student_answer.marks = score
                        student_answer.feedback = feedback
                        student_answer.save()
                        print(f"   ✅ Answer updated with new grade!")
                        
                    except Exception as e:
                        print(f"   ❌ Grading failed: {e}")
                else:
                    print("   ❌ No reference answers found - cannot auto-grade")
                    print("   💡 Create a reference answer for this question in Django admin")
            else:
                print("   ❌ No original_question set - cannot find reference answers")
        else:
            print("❌ No student answer found for this question")
    
    # Recalculate exam score
    print(f"\n--- Recalculating Exam Score ---")
    total_marks = 0
    total_questions = 0
    
    for stu_question in test_exam.questions.all():
        if stu_question.original_question:
            student_answer = SubjectiveAnswer.objects.filter( # type: ignore
                question=stu_question.original_question,
                student=test_exam.student
            ).first()
            
            if student_answer:
                total_marks += student_answer.marks
                total_questions += 1
                print(f"Question: {student_answer.marks}/5 marks")
    
    if total_questions > 0:
        average_score = (total_marks / total_questions) * 20  # Convert to percentage (5 marks = 100%)
        test_exam.score = int(average_score)
        test_exam.save()
        print(f"📊 Updated exam score: {average_score:.1f}%")
    else:
        print("❌ No questions to calculate score")

if __name__ == "__main__":
    debug_test_exam() 