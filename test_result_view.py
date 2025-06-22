#!/usr/bin/env python3
"""
Test the result view data preparation
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.contrib.auth.models import User
from student.models import StuExam_DB, SubjectiveAnswer

def test_result_view_data():
    print("🧪 Testing Result View Data Preparation")
    print("=" * 50)
    
    # Find the test exam
    test_exam = StuExam_DB.objects.filter(examname='test').first() # type: ignore
    if not test_exam:
        print("❌ Test exam not found!")
        return
    
    student = test_exam.student
    print(f"✅ Found test exam: {test_exam.examname}")
    print(f"   Student: {student.username}")
    print(f"   Score: {test_exam.score}%")
    print(f"   Questions: {test_exam.questions.count()}")
    
    # Simulate the result view logic
    questions_with_answers = []
    for stu_question in test_exam.questions.all():
        original_question = stu_question.original_question
        if not original_question:
            original_question = stu_question.question
            
        student_answer = SubjectiveAnswer.objects.filter( # type: ignore
            question=original_question,
            student=student
        ).first()
        
        questions_with_answers.append({
            'question': stu_question,
            'answer': student_answer
        })
        
        print(f"\n--- Question Analysis ---")
        print(f"Question: {stu_question.question}")
        print(f"Original question: {original_question}")
        print(f"Student answer found: {student_answer is not None}")
        
        if student_answer:
            print(f"   Text answer: {student_answer.text_answer}")
            print(f"   Image answer: {student_answer.image_answer}")
            print(f"   OCR text: {student_answer.ocr_text}")
            print(f"   Marks: {student_answer.marks}/5")
            print(f"   Feedback: {student_answer.feedback}")
        else:
            print(f"   ❌ No answer found!")
    
    print(f"\n📊 Summary:")
    print(f"   Questions with answers: {len([q for q in questions_with_answers if q['answer']])}")
    print(f"   Questions without answers: {len([q for q in questions_with_answers if not q['answer']])}")
    
    return questions_with_answers

if __name__ == "__main__":
    test_result_view_data() 