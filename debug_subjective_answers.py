#!/usr/bin/env python3
"""
Debug script to check SubjectiveAnswer records
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.models import SubjectiveAnswer, StuExam_DB, Stu_Question
from main.models import Exam_Model, Question_DB
from django.contrib.auth.models import User

def debug_subjective_answers():
    print("=== DEBUGGING SUBJECTIVE ANSWERS ===\n")
    
    # Check if there are any SubjectiveAnswer records
    all_answers = SubjectiveAnswer.objects.all() # type: ignore
    print(f"Total SubjectiveAnswer records: {all_answers.count()}")
    
    if all_answers.count() > 0:
        print("\n--- All SubjectiveAnswer Records ---")
        for answer in all_answers:
            print(f"ID: {answer.id}")
            print(f"Student: {answer.student.username}")
            print(f"Question: {answer.question.question[:50]}...")
            print(f"Text Answer: {answer.text_answer[:50] if answer.text_answer else 'None'}...")
            print(f"Image Answer: {answer.image_answer}")
            print(f"OCR Text: {answer.ocr_text[:50] if answer.ocr_text else 'None'}...")
            print(f"Marks: {answer.marks}")
            print(f"Feedback: {answer.feedback}")
            print("---")
    
    # Check StuExam_DB records
    print(f"\nTotal StuExam_DB records: {StuExam_DB.objects.count()}") # type: ignore
    completed_exams = StuExam_DB.objects.filter(completed=1) # type: ignore
    print(f"Completed exams: {completed_exams.count()}")
    
    if completed_exams.count() > 0:
        print("\n--- Completed Exams ---")
        for exam in completed_exams:
            print(f"Exam: {exam.examname}")
            print(f"Student: {exam.student.username}")
            print(f"Questions count: {exam.questions.count()}")
            
            # Check each question
            for stu_question in exam.questions.all():
                print(f"  Question: {stu_question.question[:50]}...")
                print(f"  Original question: {stu_question.original_question}")
                
                # Try to find SubjectiveAnswer
                if stu_question.original_question:
                    subj_answer = SubjectiveAnswer.objects.filter( # type: ignore   
                        question=stu_question.original_question,
                        student=exam.student
                    ).first()
                    print(f"  Found SubjectiveAnswer: {subj_answer is not None}")
                    if subj_answer:
                        print(f"  Answer content: {subj_answer.text_answer or subj_answer.ocr_text}")
                else:
                    print(f"  No original_question set!")
                print("  ---")
    
    # Check Exam_Model records
    print(f"\nTotal Exam_Model records: {Exam_Model.objects.count()}") # type: ignore
    exams = Exam_Model.objects.all() # type: ignore
    for exam in exams:
        print(f"Exam: {exam.name}")
        print(f"Professor: {exam.professor.username}")
        print(f"Question Paper: {exam.question_paper.qPaperTitle}")
        print("---")

if __name__ == "__main__":
    debug_subjective_answers() 