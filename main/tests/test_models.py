"""
Unit tests for main app models
"""
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from main.models import Question_DB, Question_Paper, Exam_Model, ReferenceAnswer
from main.models.group import Special_Students
import logging

logger = logging.getLogger(__name__)


class QuestionDBModelTest(TestCase):
    """Test cases for Question_DB model"""
    
    def setUp(self):
        """Set up test data"""
        self.professor_group = Group.objects.create(name="Professor")
        self.professor = User.objects.create_user(
            username='test_professor',
            email='prof@test.com',
            password='testpass123'
        )
        self.professor.groups.add(self.professor_group)
    
    def test_question_creation(self):
        """Test question creation with valid data"""
        question = Question_DB.objects.create(
            professor=self.professor,
            question="What is the capital of France?",
            question_type="SUBJECTIVE"
        )
        
        self.assertEqual(question.question, "What is the capital of France?")
        self.assertEqual(question.question_type, "SUBJECTIVE")
        self.assertEqual(question.professor, self.professor)
        self.assertIsNotNone(question.qno)
    
    def test_question_str_representation(self):
        """Test string representation of question"""
        question = Question_DB.objects.create(
            professor=self.professor,
            question="What is the capital of France?",
            question_type="SUBJECTIVE"
        )
        
        expected = f"Question No.{question.qno}: What is the capital of France?"
        self.assertEqual(str(question), expected)
    
    def test_question_str_with_long_text(self):
        """Test string representation with long question text"""
        long_question = "What is the capital of France? " * 10
        question = Question_DB.objects.create(
            professor=self.professor,
            question=long_question,
            question_type="SUBJECTIVE"
        )
        
        self.assertTrue(str(question).endswith("..."))
        self.assertLessEqual(len(str(question)), 70)  # qno + ": " + 50 chars + "..."
    
    def test_question_deletion_protection(self):
        """Test that question deletion is protected outside admin"""
        question = Question_DB.objects.create(
            professor=self.professor,
            question="Test question",
            question_type="SUBJECTIVE"
        )
        
        with self.assertRaises(Exception) as context:
            question.delete()
        
        self.assertIn("Deletion of questions is not allowed", str(context.exception))
    
    def test_question_deletion_with_force(self):
        """Test that question deletion works with force_delete"""
        question = Question_DB.objects.create(
            professor=self.professor,
            question="Test question",
            question_type="SUBJECTIVE"
        )
        
        question_id = question.qno
        question.delete(force_delete=True)
        
        self.assertFalse(Question_DB.objects.filter(qno=question_id).exists())


class QuestionPaperModelTest(TestCase):
    """Test cases for Question_Paper model"""
    
    def setUp(self):
        """Set up test data"""
        self.professor_group = Group.objects.create(name="Professor")
        self.professor = User.objects.create_user(
            username='test_professor',
            email='prof@test.com',
            password='testpass123'
        )
        self.professor.groups.add(self.professor_group)
        
        self.question = Question_DB.objects.create(
            professor=self.professor,
            question="Test question",
            question_type="SUBJECTIVE"
        )
    
    def test_question_paper_creation(self):
        """Test question paper creation"""
        paper = Question_Paper.objects.create(
            professor=self.professor,
            qPaperTitle="Test Paper",
            total_questions=1
        )
        paper.questions.add(self.question)
        
        self.assertEqual(paper.qPaperTitle, "Test Paper")
        self.assertEqual(paper.total_questions, 1)
        self.assertEqual(paper.questions.count(), 1)
        self.assertIn(self.question, paper.questions.all())


class ExamModelTest(TestCase):
    """Test cases for Exam_Model"""
    
    def setUp(self):
        """Set up test data"""
        self.professor_group = Group.objects.create(name="Professor")
        self.professor = User.objects.create_user(
            username='test_professor',
            email='prof@test.com',
            password='testpass123'
        )
        self.professor.groups.add(self.professor_group)
        
        self.question = Question_DB.objects.create(
            professor=self.professor,
            question="Test question",
            question_type="SUBJECTIVE"
        )
        
        self.paper = Question_Paper.objects.create(
            professor=self.professor,
            qPaperTitle="Test Paper",
            total_questions=1
        )
        self.paper.questions.add(self.question)
        
        self.student_group = Special_Students.objects.create(
            professor=self.professor,
            category_name="Test Group"
        )
    
    def test_exam_creation(self):
        """Test exam creation with valid data"""
        exam = Exam_Model.objects.create(
            professor=self.professor,
            name="Test Exam",
            total_marks=100,
            duration=60,
            question_paper=self.paper
        )
        exam.student_group.add(self.student_group)
        
        self.assertEqual(exam.name, "Test Exam")
        self.assertEqual(exam.total_marks, 100)
        self.assertEqual(exam.duration, 60)
        self.assertEqual(exam.question_paper, self.paper)
        self.assertIn(self.student_group, exam.student_group.all())


class ReferenceAnswerModelTest(TestCase):
    """Test cases for ReferenceAnswer model"""
    
    def setUp(self):
        """Set up test data"""
        self.professor_group = Group.objects.create(name="Professor")
        self.professor = User.objects.create_user(
            username='test_professor',
            email='prof@test.com',
            password='testpass123'
        )
        self.professor.groups.add(self.professor_group)
        
        self.question = Question_DB.objects.create(
            professor=self.professor,
            question="What is the capital of France?",
            question_type="SUBJECTIVE"
        )
    
    def test_reference_answer_creation(self):
        """Test reference answer creation"""
        ref_answer = ReferenceAnswer.objects.create(
            question=self.question,
            text_answer="Paris is the capital of France.",
            professor=self.professor
        )
        
        self.assertEqual(ref_answer.question, self.question)
        self.assertEqual(ref_answer.text_answer, "Paris is the capital of France.")
        self.assertEqual(ref_answer.professor, self.professor)
    
    def test_reference_answer_str_representation(self):
        """Test string representation of reference answer"""
        ref_answer = ReferenceAnswer.objects.create(
            question=self.question,
            text_answer="Paris is the capital of France.",
            professor=self.professor
        )
        
        expected = f"Reference for Q{self.question.qno}: Paris is the capital of France."
        self.assertEqual(str(ref_answer), expected)


class ModelValidationTest(TestCase):
    """Test model validation and constraints"""
    
    def setUp(self):
        """Set up test data"""
        self.professor_group = Group.objects.create(name="Professor")
        self.professor = User.objects.create_user(
            username='test_professor',
            email='prof@test.com',
            password='testpass123'
        )
        self.professor.groups.add(self.professor_group)
    
    def test_question_max_length_validation(self):
        """Test question text length validation"""
        # Create a question with maximum allowed length
        long_question = "A" * 1000  # Max length is 1000
        question = Question_DB.objects.create(
            professor=self.professor,
            question=long_question,
            question_type="SUBJECTIVE"
        )
        
        self.assertEqual(len(question.question), 1000)
    
    def test_question_type_choices(self):
        """Test question type choices validation"""
        question = Question_DB.objects.create(
            professor=self.professor,
            question="Test question",
            question_type="SUBJECTIVE"  # Valid choice
        )
        
        self.assertEqual(question.question_type, "SUBJECTIVE")
        
        # Test default value
        question2 = Question_DB.objects.create(
            professor=self.professor,
            question="Test question 2"
        )
        
        self.assertEqual(question2.question_type, "SUBJECTIVE")


class ModelPerformanceTest(TestCase):
    """Test model performance and database queries"""
    
    def setUp(self):
        """Set up test data"""
        self.professor_group = Group.objects.create(name="Professor")
        self.professor = User.objects.create_user(
            username='test_professor',
            email='prof@test.com',
            password='testpass123'
        )
        self.professor.groups.add(self.professor_group)
    
    def test_bulk_question_creation(self):
        """Test bulk creation of questions for performance"""
        questions_data = [
            Question_DB(
                professor=self.professor,
                question=f"Test question {i}",
                question_type="SUBJECTIVE"
            )
            for i in range(100)
        ]
        
        Question_DB.objects.bulk_create(questions_data)
        
        self.assertEqual(Question_DB.objects.count(), 100)
    
    def test_question_filtering_performance(self):
        """Test filtering questions by professor"""
        # Create multiple questions
        for i in range(50):
            Question_DB.objects.create(
                professor=self.professor,
                question=f"Test question {i}",
                question_type="SUBJECTIVE"
            )
        
        # Test filtering
        professor_questions = Question_DB.objects.filter(professor=self.professor)
        self.assertEqual(professor_questions.count(), 50)
