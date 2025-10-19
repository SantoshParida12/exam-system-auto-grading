from django.db import models
from django.contrib.auth.models import User
from .question import Question_DB

class ReferenceAnswer(models.Model):
    question = models.ForeignKey(Question_DB, on_delete=models.PROTECT, related_name='reference_answers')
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE)
    
    # Reference answer can be either text or image
    text_answer = models.TextField(blank=True, null=True, help_text="Reference text answer")
    image_answer = models.ImageField(upload_to='reference_answers/', blank=True, null=True, help_text="Reference handwritten answer image")
    
    # OCR extracted text from the image
    ocr_text = models.TextField(blank=True, null=True, help_text="OCR extracted text from reference image")
    
    # TF-IDF vector (stored as JSON for similarity comparison)
    tfidf_vector = models.JSONField(blank=True, null=True, help_text="TF-IDF vector for similarity comparison")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['question', 'professor']
        verbose_name = "Reference Answer"
        verbose_name_plural = "Reference Answers"
    
    def __str__(self):
        return f"Reference Answer for Q{self.question.qno} by {self.professor.username}" # type: ignore
    
    def process_ocr(self):
        """
        Manually process OCR for this reference answer
        """
        if self.image_answer:
            print(f"Manually processing OCR for reference answer {self.pk}")
            from student.utils import extract_text_from_image
            ocr_text, error = extract_text_from_image(self.image_answer)
            if ocr_text:
                self.ocr_text = ocr_text
                print(f"OCR successful: '{ocr_text[:100]}...'")
                return True
            else:
                print(f"OCR failed: {error}")
                return False
        return False
    
    def save(self, *args, **kwargs):
        print(f"ReferenceAnswer.save() called for question {self.question.qno}") # type: ignore
        print(f"  - Has image: {bool(self.image_answer)}")
        print(f"  - Has text: {bool(self.text_answer)}")
        print(f"  - Current OCR text: {self.ocr_text}")
        
        # If image is uploaded, always process OCR (even if OCR text exists)
        if self.image_answer:
            print(f"  - Processing OCR for image: {self.image_answer}")
            from student.utils import extract_text_from_image
            ocr_text, error = extract_text_from_image(self.image_answer)
            if ocr_text:
                self.ocr_text = ocr_text
                print(f"  - OCR successful: '{ocr_text[:100]}...'")
            else:
                print(f"  - OCR failed: {error}")
                # Don't clear existing OCR text if OCR fails
                if not self.ocr_text:
                    self.ocr_text = f"OCR processing failed: {error}"
        
        # Generate TF-IDF vector for similarity comparison
        if self.text_answer or self.ocr_text:
            print(f"  - Generating TF-IDF vector")
            from student.utils import generate_tfidf_vector
            text_content = self.text_answer or self.ocr_text or ""
            self.tfidf_vector = generate_tfidf_vector(text_content)
            if self.tfidf_vector:
                print(f"  - TF-IDF vector generated successfully")
            else:
                print(f"  - TF-IDF vector generation failed")
        else:
            print(f"  - No text content for TF-IDF")
        
        super().save(*args, **kwargs) 