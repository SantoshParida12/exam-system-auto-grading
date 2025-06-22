from pickletools import int4
from django.db import models
from main.models import *
from django.contrib.auth.models import User

# Create your models here.
class Stu_Question(Question_DB):
    professor = None
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    original_question = models.ForeignKey(Question_DB, on_delete=models.CASCADE, null=True, related_name='student_questions')


class StuExam_DB(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    examname = models.CharField(max_length=100)
    qpaper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE, null=True)
    questions = models.ManyToManyField(Stu_Question)
    score = models.IntegerField(default=int)  # pyright: ignore
    completed = models.IntegerField(default=int)  # pyright: ignore


class StuResults_DB(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    exams = models.ManyToManyField(StuExam_DB)


class SubjectiveAnswer(models.Model):
    question = models.ForeignKey(Question_DB, on_delete=models.CASCADE)
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    image_answer = models.ImageField(upload_to='subjective_answers/', blank=True, null=True)
    ocr_text = models.TextField(blank=True, null=True)
    marks = models.IntegerField(default=0, help_text="Marks awarded (0-5)")  # type: ignore
    feedback = models.TextField(blank=True, null=True, help_text="Automated feedback based on TF-IDF analysis")
    submitted_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Subjective Answer by {self.student} for Q{self.question_id}'# type: ignore
