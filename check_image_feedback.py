#!/usr/bin/env python3
"""
Check if image answers are receiving proper feedback
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from student.models import SubjectiveAnswer
from student.utils import grade_answer, get_reference_answers_for_question

def check_image_feedback():
    print("📝 Checking Image Answer Feedback")
    print("=" * 40)
    
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
        
        # Check current feedback
        print(f"Current feedback: {answer.feedback}")
        print(f"Current marks: {answer.marks}/5")
        
        # Check if OCR text exists
        if answer.ocr_text:
            print(f"OCR text: '{answer.ocr_text[:100]}...'")
        else:
            print(f"❌ No OCR text found!")
            continue
        
        # Check for reference answers
        reference_answers = get_reference_answers_for_question(answer.question)
        print(f"Reference answers found: {reference_answers.count()}")
        
        if reference_answers.count() > 0:
            # Re-grade to ensure feedback is generated
            marks, feedback, best_ref = grade_answer(answer, reference_answers)
            print(f"📊 Re-grading result: {marks}/5 marks")
            print(f"📝 Generated feedback: {feedback}")
            
            # Update if feedback is missing or different
            if not answer.feedback or answer.feedback != feedback:
                answer.marks = marks
                answer.feedback = feedback
                answer.save()
                print(f"✅ Updated answer with new feedback!")
            else:
                print(f"ℹ️  Feedback already exists and is correct")
        else:
            print(f"❌ No reference answers - cannot generate feedback")
    
    print(f"\n📊 Summary:")
    print(f"   Image answers with feedback: {image_answers.filter(feedback__isnull=False).exclude(feedback='').count()}")
    print(f"   Image answers without feedback: {image_answers.filter(feedback__isnull=True).count() + image_answers.filter(feedback='').count()}")

if __name__ == "__main__":
    check_image_feedback() 