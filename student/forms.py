from django import forms
from .models import SubjectiveAnswer
from .utils import extract_text_from_image, validate_image_file

class SubjectiveAnswerForm(forms.ModelForm):
    class Meta:
        model = SubjectiveAnswer
        fields = ['text_answer', 'image_answer']
        widgets = {
            'text_answer': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Type your answer here...'
            }),
            'image_answer': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*',
                'id': 'image-upload'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text_answer')
        image = cleaned_data.get('image_answer')
        
        if not text and not image:
            raise forms.ValidationError('You must provide either a text answer or an image answer.')
        
        # Process image if uploaded
        if image:
            # Validate image file
            is_valid, error_msg = validate_image_file(image)
            if not is_valid:
                raise forms.ValidationError(error_msg)
            
            # Extract text from image using OCR
            ocr_text, ocr_error = extract_text_from_image(image)
            if ocr_error:
                # Don't fail the form if OCR fails, just log it
                print(f"OCR Error: {ocr_error}")
                ocr_text = "OCR processing failed. Please check your image quality."
            
            # Store OCR text in cleaned_data
            cleaned_data['ocr_text'] = ocr_text
        
        return cleaned_data 