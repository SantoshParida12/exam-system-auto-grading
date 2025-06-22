#!/usr/bin/env python3
"""
Mark all exams as completed if they have at least one graded answer
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.models import StuExam_DB, SubjectiveAnswer

def mark_completed_exams():
    print("🔄 Marking completed exams...")
    exams = StuExam_DB.objects.all() # type: ignore
    updated = 0
    for exam in exams:
        # Check if any answer for this exam's questions is graded
        has_graded = False
        for stu_question in exam.questions.all():
            answer = SubjectiveAnswer.objects.filter(question=stu_question.original_question, student=exam.student).first() # type: ignore
            if answer and answer.marks > 0:
                has_graded = True
                break
        if has_graded and exam.completed != 1:
            exam.completed = 1
            exam.save()
            print(f"✅ Marked exam '{exam.examname}' for student '{exam.student.username}' as completed.")
            updated += 1
    print(f"\nDone! {updated} exams marked as completed.")

if __name__ == "__main__":
    mark_completed_exams() 