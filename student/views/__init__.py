from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from main.models import *
from django.contrib.auth.models import User
from student.models import *
from django.contrib.auth.decorators import login_required

from .exams import *
from .result import *

# Create your views here.

@login_required
def index(request):
    student = request.user

    studentGroup = Special_Students.objects.filter(students=student)  # type: ignore
    examsList = []
    if studentGroup.exists():
        for student_ in studentGroup:
            stud_exams = Exam_Model.objects.filter(student_group=student_)  # type: ignore
            if stud_exams.exists():
                if stud_exams.count() > 1:
                    for stud_exam in stud_exams:
                        examsList.append(stud_exam)
                else:
                    examsList.append(Exam_Model.objects.get(  # type: ignore
                        student_group=student_))

    if examsList:
        for exam in examsList:
            currentExamList = StuExam_DB.objects.filter(  # type: ignore
                examname=exam.name, student=student)

            if not currentExamList.exists():  # If no exam are there in then add exams
                tempExam = StuExam_DB(student=student, examname=exam.name,
                                        qpaper=exam.question_paper, score=0, completed=0)
                tempExam.save()
                exam_question_paper = exam.question_paper
                questions_in_paper = exam_question_paper.questions.all()
                
                for ques in questions_in_paper:
                    # add all the questions from the prof to student database
                    studentQuestion = Stu_Question.objects.create(#type: ignore
                        qno=ques.qno,
                        question=ques.question,
                        question_type=ques.question_type,
                        student=student,
                        original_question=ques
                    )
                    tempExam.questions.add(studentQuestion)  # type: ignore
                    tempExam.save()

    return render(request, 'student/index.html', {
        'student': student, 'examsList': examsList
    })
