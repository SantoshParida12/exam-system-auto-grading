#!/usr/bin/env python3
"""
Test image answer processing and grading
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.contrib.auth.models import User
from student.models import SubjectiveAnswer, StuExam_DB
from student.utils import extract_text_from_image, grade_answer, get_reference_answers_for_question
from main.models import Question_DB, ReferenceAnswer

def test_image_grading():
    print("🖼️ Testing Image Answer Processing and Grading")
    print("=" * 55)
    
    # Find all image answers
    image_answers = SubjectiveAnswer.objects.filter(image_answer__isnull=False) # type: ignore
    print(f"Found {image_answers.count()} image answers")
    
    if image_answers.count() == 0:
        print("❌ No image answers found!")
        return
    
    for answer in image_answers:
        print(f"\n--- Image Answer {answer.id} ---")
        print(f"Student: {answer.student.username}")
        print(f"Question: {answer.question.question[:50]}...")
        print(f"Image file: {answer.image_answer}")
        
        # Check if OCR text exists
        if answer.ocr_text:
            print(f"✅ OCR text exists: '{answer.ocr_text[:100]}...'")
        else:
            print(f"❌ No OCR text - processing now...")
            # Process OCR
            ocr_text, ocr_error = extract_text_from_image(answer.image_answer)
            if ocr_text:
                answer.ocr_text = ocr_text
                answer.save()
                print(f"✅ OCR processed: '{ocr_text[:100]}...'")
            else:
                print(f"❌ OCR failed: {ocr_error}")
                continue
        
        # Check for reference answers
        reference_answers = get_reference_answers_for_question(answer.question)
        print(f"Reference answers found: {reference_answers.count()}") # type: ignore
        
        if reference_answers.count() > 0: # type: ignore
            # Grade the answer
            marks, feedback, best_ref = grade_answer(answer, reference_answers)
            print(f"📊 Grading result: {marks}/5 marks")
            print(f"📝 Feedback: {feedback}")
            
            # Update the answer if marks changed
            if answer.marks != marks:
                answer.marks = marks
                answer.feedback = feedback
                answer.save()
                print(f"✅ Answer updated with new grade!")
            else:
                print(f"ℹ️  Grade already set: {answer.marks}/5")
        else:
            print(f"❌ No reference answers - cannot grade")
    
    # Check exam scores
    print(f"\n📊 Checking Exam Scores...")
    exams = StuExam_DB.objects.filter(completed=1) # type: ignore
    for exam in exams:
        print(f"\nExam: {exam.examname} (Student: {exam.student.username})")
        print(f"Current score: {exam.score}%")
        
        # Recalculate score
        total_marks = 0
        total_questions = 0
        
        for stu_question in exam.questions.all():
            if stu_question.original_question:
                answer = SubjectiveAnswer.objects.filter( # type: ignore
                    question=stu_question.original_question,
                    student=exam.student
                ).first()
                
                if answer:
                    total_marks += answer.marks
                    total_questions += 1
                    print(f"  Q: {answer.marks}/5 marks")
        
        if total_questions > 0:
            average_score = total_marks / total_questions
            percentage_score = (average_score / 5) * 100
            exam.score = int(percentage_score)
            exam.save()
            print(f"📊 Updated score: {percentage_score:.1f}%")

if __name__ == "__main__":
    test_image_grading() 