#!/usr/bin/env python3
"""
Create reference answer for the test question
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Question_DB, ReferenceAnswer

def create_reference_answer():
    print("📝 CREATING REFERENCE ANSWER FOR TEST QUESTION")
    print("=" * 50)
    
    # Find the test question
    test_question = Question_DB.objects.filter(qno=120).first() # type: ignore
    if not test_question:
        print("❌ Test question (Q120) not found!")
        return False
    
    print(f"✅ Found test question: {test_question.question}")
    
    # Find a professor
    professor = User.objects.filter(groups__name='Professor').first()
    if not professor:
        print("❌ No professor found!")
        return False
    
    print(f"✅ Found professor: {professor.username}")
    
    # Check if reference answer already exists
    existing_ref = ReferenceAnswer.objects.filter( # type: ignore
        question=test_question,
        professor=professor
    ).first()
    
    if existing_ref:
        print(f"✅ Reference answer already exists!")
        print(f"   Text: {existing_ref.text_answer}")
        print(f"   Marks: {existing_ref.marks if hasattr(existing_ref, 'marks') else 'N/A'}")
        return True
    
    # Create reference answer
    reference_text = "My name is [Student Name]"
    
    ref_answer = ReferenceAnswer.objects.create( # type: ignore
        question=test_question,
        professor=professor,
        text_answer=reference_text
    )
    
    print(f"✅ Created reference answer:")
    print(f"   Question: {ref_answer.question.question}")
    print(f"   Professor: {ref_answer.professor.username}")
    print(f"   Text Answer: {ref_answer.text_answer}")
    
    return True

if __name__ == "__main__":
    success = create_reference_answer()
    if success:
        print("\n🎉 Reference answer created successfully!")
        print("💡 Now run the auto-grading test to see if it works:")
        print("   python test_auto_grading.py")
    else:
        print("\n❌ Failed to create reference answer") 