from student.serializers import *
from student.models import StuExam_DB, Stu_Question
from main.serializers import Question_PaperSerializer
from main.models import Exam_Model

from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils import timezone
from django.contrib.auth.models import User


class Exam(APIView):
    def get(self, request, pk):
        student = User.objects.get(pk=pk)
        studentExamsList = StuExam_DB.objects.filter(student=student)  # type: ignore

        return Response({
            'student': UserSerializer(student).data, 
            'paper': StuExam_DBSerializer(studentExamsList, many=True).data
        })

    
    def post(self, request, pk):
        student = User.objects.get(pk=pk)

        if not request.POST.get('papertitle', False):
            paper = request.POST['paper']
            stuExam = StuExam_DB.objects.get(examname=paper, student=student)  # type: ignore
            qPaper = stuExam.qpaper
            examMain = Exam_Model.objects.get(name=paper)  # type: ignore

            # TIME COMPARISON
            exam_start_time = examMain.start_time
            curr_time = timezone.now()

            if curr_time < exam_start_time:
                return Response({'time': 'Time expired'})


            stuExam.questions.all().delete()

            qPaperQuestionsList = qPaper.questions.all()
            for ques in qPaperQuestionsList:
                student_question = Stu_Question(question=ques.question, student=student)
                student_question.save()
                stuExam.questions.add(student_question)
                stuExam.save()

            stuExam.completed = 1
            stuExam.save()
            mins = examMain.duration
            secs = 0

            return Response({
                'qpaper': Question_PaperSerializer(qPaper).data, 
                'question_list': Stu_QuestionSerializer(stuExam.questions.all(), many=True).data, 
                'student': UserSerializer(student).data, 
                'exam': paper, 
                'min': mins, 'sec': secs
            })


        else:
            paper = request.POST['paper']
            title = request.POST['papertitle']
            stuExam = StuExam_DB.objects.get(examname=paper, student=student)  # type: ignore
            qPaper = stuExam.qpaper

            # For subjective questions, we don't calculate automatic scores
            # Scores will be assigned by professors later
            stuExam.score = 0
            stuExam.save()

            return Response({
                'Title': title, 
                'Score': 'Pending Review', 
                'student': UserSerializer(student).data
            })