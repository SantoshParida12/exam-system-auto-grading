from django import forms
from main.models.exam import Exam_Model

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam_Model
        exclude = ['professor'] 