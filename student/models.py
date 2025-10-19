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
    score = models.IntegerField(default=0)
    completed = models.IntegerField(default=0)
    total_marks_possible = models.IntegerField(default=0, help_text="Total marks possible for this exam")
    percentage = models.FloatField(default=0.0, help_text="Percentage score")
    started_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True, help_text="Time taken to complete the exam")
    is_graded = models.BooleanField(default=False, help_text="Whether the exam has been graded")
    
    class Meta:
        verbose_name = "Student Exam"
        verbose_name_plural = "Student Exams"
        ordering = ['-completed_at', '-started_at']
    
    def save(self, *args, **kwargs):
        # Calculate percentage if we have both score and total marks
        if self.total_marks_possible > 0:
            self.percentage = (self.score / self.total_marks_possible) * 100
        super().save(*args, **kwargs)
    
    def get_grade_letter(self):
        """Return letter grade based on percentage"""
        if self.percentage >= 90:
            return 'A+'
        elif self.percentage >= 80:
            return 'A'
        elif self.percentage >= 70:
            return 'B+'
        elif self.percentage >= 60:
            return 'B'
        elif self.percentage >= 50:
            return 'C+'
        elif self.percentage >= 40:
            return 'C'
        elif self.percentage >= 30:
            return 'D'
        else:
            return 'F'
    
    def __str__(self):
        return f"{self.student.username} - {self.examname} ({self.score}/{self.total_marks_possible})"


class StuResults_DB(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    exams = models.ManyToManyField(StuExam_DB)


class ExamResults(models.Model):
    """Model to store comprehensive exam results and statistics"""
    exam = models.ForeignKey(Exam_Model, on_delete=models.CASCADE)
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE)
    student_exam = models.OneToOneField(StuExam_DB, on_delete=models.CASCADE)
    
    # Overall exam statistics
    total_questions = models.IntegerField(default=0)
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    questions_partial = models.IntegerField(default=0)
    questions_incorrect = models.IntegerField(default=0)
    
    # Scoring details
    total_score = models.IntegerField(default=0)
    max_possible_score = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    grade_letter = models.CharField(max_length=2, default='F')
    
    # Time and completion details
    time_taken = models.DurationField(null=True, blank=True)
    completion_rate = models.FloatField(default=0.0, help_text="Percentage of questions attempted")
    accuracy_rate = models.FloatField(default=0.0, help_text="Percentage of correct answers")
    
    # Status flags
    is_completed = models.BooleanField(default=False)
    is_graded = models.BooleanField(default=False)
    is_passed = models.BooleanField(default=False, help_text="Whether student passed the exam")
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Exam Result"
        verbose_name_plural = "Exam Results"
        ordering = ['-completed_at', '-started_at']
        unique_together = ['exam', 'student']
    
    def save(self, *args, **kwargs):
        # Calculate derived fields
        if self.max_possible_score > 0:
            self.percentage = (self.total_score / self.max_possible_score) * 100
        
        if self.total_questions > 0:
            self.completion_rate = (self.questions_attempted / self.total_questions) * 100
            self.accuracy_rate = (self.questions_correct / self.questions_attempted) * 100 if self.questions_attempted > 0 else 0
        
        # Determine grade letter
        if self.percentage >= 90:
            self.grade_letter = 'A+'
        elif self.percentage >= 80:
            self.grade_letter = 'A'
        elif self.percentage >= 70:
            self.grade_letter = 'B+'
        elif self.percentage >= 60:
            self.grade_letter = 'B'
        elif self.percentage >= 50:
            self.grade_letter = 'C+'
        elif self.percentage >= 40:
            self.grade_letter = 'C'
        elif self.percentage >= 30:
            self.grade_letter = 'D'
        else:
            self.grade_letter = 'F'
        
        # Determine if passed (assuming 50% is passing)
        self.is_passed = self.percentage >= 50
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.name} ({self.grade_letter})"


class SubjectiveAnswer(models.Model):
    question = models.ForeignKey(Question_DB, on_delete=models.CASCADE)
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    image_answer = models.ImageField(upload_to='subjective_answers/', blank=True, null=True)
    ocr_text = models.TextField(blank=True, null=True)
    marks = models.IntegerField(default=0, help_text="Marks awarded")
    max_marks = models.IntegerField(default=5, help_text="Maximum marks for this question")
    feedback = models.TextField(blank=True, null=True, help_text="Automated feedback based on TF-IDF analysis")
    teacher_feedback = models.TextField(blank=True, null=True, help_text="Additional feedback from teacher")
    is_auto_graded = models.BooleanField(default=False, help_text="Whether this answer was auto-graded")
    is_teacher_graded = models.BooleanField(default=False, help_text="Whether this answer was graded by teacher")
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_subjective_answers', help_text="Teacher who graded this answer")
    
    class Meta:
        verbose_name = "Subjective Answer"
        verbose_name_plural = "Subjective Answers"
        ordering = ['-submitted_at']
        unique_together = ['question', 'student']  # One answer per question per student
    
    def get_percentage(self):
        """Calculate percentage score for this answer"""
        if self.max_marks > 0:
            return (self.marks / self.max_marks) * 100
        return 0.0
    
    def is_passing(self, passing_threshold=50):
        """Check if this answer meets the passing threshold"""
        return self.get_percentage() >= passing_threshold
    
    def __str__(self):
        return f'{self.student.username} - Q{self.question.qno} ({self.marks}/{self.max_marks})'
