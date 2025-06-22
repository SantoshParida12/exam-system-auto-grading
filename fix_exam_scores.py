#!/usr/bin/env python3
"""
Fix existing exam scores and mark exams as completed
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.models import StuExam_DB, SubjectiveAnswer

def fix_exam_scores():
    print("🔧 Fixing exam scores and completion status...")
    exams = StuExam_DB.objects.all() # type: ignore
    fixed = 0
    
    for exam in exams:
        print(f"\n--- Processing exam: {exam.examname} (Student: {exam.student.username}) ---")
        
        total_marks = 0
        total_questions = 0
        has_answers = False
        
        for stu_question in exam.questions.all():
            if stu_question.original_question:
                answer = SubjectiveAnswer.objects.filter( # type: ignore
                    question=stu_question.original_question, 
                    student=exam.student
                ).first()
                
                if answer:
                    has_answers = True
                    total_marks += answer.marks
                    total_questions += 1
                    print(f"  Q: {answer.marks}/5 marks")
        
        if has_answers:
            # Mark as completed
            if exam.completed != 1:
                exam.completed = 1
                print(f"  ✅ Marked as completed")
            
            # Fix score calculation
            if total_questions > 0:
                average_score = total_marks / total_questions
                percentage_score = (average_score / 5) * 100
                exam.score = int(percentage_score)
                print(f"  📊 Score: {average_score:.1f}/5 = {percentage_score:.1f}%")
            else:
                exam.score = 0
                print(f"  📊 Score: 0% (no graded questions)")
            
            exam.save()
            fixed += 1
        else:
            print(f"  ❌ No answers found - keeping as incomplete")
    
    print(f"\n✅ Fixed {fixed} exams!")

if __name__ == "__main__":
    fix_exam_scores() 