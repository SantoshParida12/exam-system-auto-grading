#!/usr/bin/env python3
"""
Diagnostic script to check auto-grading status
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Question_DB, ReferenceAnswer
from student.models import SubjectiveAnswer, StuExam_DB
from student.utils import get_reference_answers_for_question

def check_auto_grading_status():
    print("🔍 AUTO-GRADING DIAGNOSTIC REPORT")
    print("=" * 50)
    
    # Check 1: Are there any questions in the system?
    questions = Question_DB.objects.all()
    print(f"\n1. Questions in system: {questions.count()}")
    
    if questions.count() == 0:
        print("   ❌ No questions found! Create questions first.")
        return
    
    # Check 2: Are there any reference answers?
    reference_answers = ReferenceAnswer.objects.all()
    print(f"\n2. Reference answers in system: {reference_answers.count()}")
    
    if reference_answers.count() == 0:
        print("   ❌ No reference answers found!")
        print("   📝 Professors need to create reference answers for auto-grading to work.")
        print("   💡 To create reference answers:")
        print("      - Go to Django admin panel")
        print("      - Navigate to 'Reference Answers'")
        print("      - Add reference answers for each question")
        print("      - Include either text or image answers")
    else:
        print("   ✅ Reference answers found!")
        for ref in reference_answers[:3]:  # Show first 3
            print(f"      - Q{ref.question.qno}: {ref.question.question[:50]}...")
        if reference_answers.count() > 3:
            print(f"      ... and {reference_answers.count() - 3} more")
    
    # Check 3: Are there any student answers?
    student_answers = SubjectiveAnswer.objects.all()
    print(f"\n3. Student answers in system: {student_answers.count()}")
    
    if student_answers.count() == 0:
        print("   ❌ No student answers found!")
        print("   📝 Students need to submit answers first.")
    else:
        print("   ✅ Student answers found!")
        
        # Check which answers have grades
        graded_answers = student_answers.filter(marks__gt=0)
        ungraded_answers = student_answers.filter(marks=0)
        
        print(f"      - Graded answers: {graded_answers.count()}")
        print(f"      - Ungraded answers: {ungraded_answers.count()}")
        
        if ungraded_answers.count() > 0:
            print("\n   📊 Ungraded answers analysis:")
            for answer in ungraded_answers[:3]:
                ref_answers = get_reference_answers_for_question(answer.question)
                print(f"      - Student {answer.student.username}, Q{answer.question.qno}")
                print(f"        Reference answers available: {ref_answers.count()}")
                if ref_answers.count() == 0:
                    print(f"        ❌ No reference answers for this question!")
                else:
                    print(f"        ✅ Reference answers exist - should auto-grade")
    
    # Check 4: Are there any completed exams?
    completed_exams = StuExam_DB.objects.filter(completed=1)
    print(f"\n4. Completed exams: {completed_exams.count()}")
    
    if completed_exams.count() == 0:
        print("   ❌ No completed exams found!")
        print("   📝 Students need to complete exams first.")
    else:
        print("   ✅ Completed exams found!")
        for exam in completed_exams:
            print(f"      - {exam.examname} (Student: {exam.student.username}, Score: {exam.score}%)")
    
    # Summary and recommendations
    print(f"\n📋 SUMMARY & RECOMMENDATIONS:")
    print("=" * 50)
    
    if reference_answers.count() == 0:
        print("❌ AUTO-GRADING NOT WORKING: No reference answers")
        print("💡 SOLUTION: Professors must create reference answers")
        print("   1. Go to Django admin panel")
        print("   2. Navigate to 'Reference Answers'")
        print("   3. Add reference answers for each question")
        print("   4. Include text or image answers")
    elif student_answers.count() == 0:
        print("❌ AUTO-GRADING NOT WORKING: No student answers")
        print("💡 SOLUTION: Students must submit answers first")
    elif ungraded_answers.count() > 0:
        print("⚠️  SOME ANSWERS NOT GRADED: Missing reference answers for some questions")
        print("💡 SOLUTION: Create reference answers for all questions")
    else:
        print("✅ AUTO-GRADING SYSTEM READY!")
        print("   All student answers have been graded automatically")

if __name__ == "__main__":
    check_auto_grading_status() 