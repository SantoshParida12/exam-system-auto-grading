from django import forms
from main.models.exam import Exam_Model

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam_Model
        exclude = ['professor', 'end_time'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Midterm Exam'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '1'}),
            'question_paper': forms.Select(attrs={'class': 'form-select'}),
            'student_group': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }