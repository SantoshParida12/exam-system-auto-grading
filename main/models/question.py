from django.db import models
from django.forms import ModelForm, Textarea, Select
from django.contrib.auth.models import User

class Question_DB(models.Model):
    # added question number for help in question paper
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE, null=True)
    qno = models.AutoField(primary_key=True)
    question = models.TextField(max_length=1000)  # Changed from CharField to TextField for longer questions
    question_type = models.CharField(max_length=20, choices=[('SUBJECTIVE', 'Subjective')], default='SUBJECTIVE')
    question_image = models.ImageField(upload_to='question_images/', null=True, blank=True)

    def __str__(self):
        question_text = str(self.question)
        return f'Question No.{self.qno}: {question_text[:50]}...' if len(question_text) > 50 else f'Question No.{self.qno}: {question_text}'


class QForm(ModelForm):
    class Meta:
        model = Question_DB
        fields = '__all__'
        exclude = ['qno', 'professor']
        widgets = {
            'question': Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Enter your question here...'
            }),
            'question_type': Select(attrs={
                'class': 'form-control'
            })
        }
