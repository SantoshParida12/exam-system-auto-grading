from django.shortcuts import render, redirect
from main.models.group import Special_Students
from main.models.question_paper import Question_Paper
from main.models.exam import Exam_Model
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from student.models import StuExam_DB, Stu_Question, SubjectiveAnswer
from django.contrib import messages
from prof.forms import ExamForm

def view_exams(request):
    prof = request.user

    new_Form = ExamForm()
    new_Form.fields["student_group"].queryset = Special_Students.objects.filter(  # type: ignore
        professor=prof)
    new_Form.fields["question_paper"].queryset = Question_Paper.objects.filter(  # type: ignore
        professor=prof)

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.professor = prof
            # Compute end_time = start_time + duration minutes
            try:
                from datetime import timedelta
                exam.end_time = exam.start_time + timedelta(minutes=exam.duration)
            except Exception:
                pass
            exam.save()
            form.save_m2m()
            return redirect('prof:view_exams')

    exams = Exam_Model.objects.filter(professor=prof)  # type: ignore

    return render(request, 'prof/exam/view_exams.html', {
        'exams': exams, 'examform': new_Form, 'prof': prof,
    })
    

def view_exam(request, exam_id):
    prof = request.user
    exam = Exam_Model.objects.get(professor=prof, pk=exam_id)  # type: ignore
    return render(request, 'prof/exam/view_exam.html', {
        'exam': exam, 'prof': prof, 'student_group': exam.student_group.all()
    })
    

def edit_exam(request, exam_id):
    prof = request.user
    exam = Exam_Model.objects.filter(professor=prof, pk=exam_id).first()  # type: ignore
    
    new_Form = ExamForm(instance=exam)
    new_Form.fields["student_group"].queryset = Special_Students.objects.filter(professor=prof)  # type: ignore
    new_Form.fields["question_paper"].queryset = Question_Paper.objects.filter(professor=prof)  # type: ignore

    if request.method == 'POST':
        print("[DEBUG][edit_exam] POST data:", request.POST)
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            print("[DEBUG][edit_exam] Changed data:", form.changed_data)
            exam_obj = form.save(commit=False)
            try:
                from datetime import timedelta
                exam_obj.end_time = exam_obj.start_time + timedelta(minutes=exam_obj.duration)
            except Exception:
                pass
            exam_obj.save()
            form.save_m2m()
            # Ensure all student exam records use the updated question paper and questions
            from student.models import StuExam_DB, Stu_Question
            for stu_exam in StuExam_DB.objects.filter(examname=exam.name): # type: ignore
                stu_exam.qpaper = exam.question_paper
                stu_exam.questions.clear()
                for ques in exam.question_paper.questions.all():
                    stu_question = Stu_Question.objects.create( # type: ignore
                        question=ques.question,
                        question_type=ques.question_type,
                        student=stu_exam.student,
                        original_question=ques
                    )
                    stu_exam.questions.add(stu_question)
                stu_exam.save()
            return redirect('prof:view_exams')
        else:
            print("[DEBUG][edit_exam] Form errors:", form.errors)

    return render(request, 'prof/exam/edit_exam.html', {
        'form': new_Form, 'exam': exam, 'prof': prof
    })
    

def delete_exam(request, exam_id):
    prof = request.user
    exam = Exam_Model.objects.get(professor=prof, pk=exam_id)  # type: ignore
    exam.delete()
    return redirect('prof:view_exams')

def evaluate_exam(request, exam_id):
    prof = request.user
    exam = Exam_Model.objects.get(professor=prof, pk=exam_id)  # type: ignore
    # Get all student exam records for this exam that are completed
    student_exams = StuExam_DB.objects.filter(examname=exam.name, completed=1)  # type: ignore

    if request.method == 'POST':
        # Save scores for each student
        for stu_exam in student_exams:
            score_field = f'score_{stu_exam.id}'
            score = request.POST.get(score_field)
            if score is not None and score != '':
                try:
                    stu_exam.score = int(score)
                    stu_exam.save()
                except ValueError:
                    messages.error(request, f"Invalid score for student {stu_exam.student.username}")
        messages.success(request, "Scores updated successfully!")

    # Prepare data for template
    student_data = []
    for stu_exam in student_exams:
        answers = []
        for stu_question in stu_exam.questions.all():
            # Get the original question object
            original_question = stu_question.original_question
            if not original_question:
                # Fallback to the question field if original_question is not set
                original_question = stu_question.question
            
            # Query SubjectiveAnswer using the original question object
            subj_answer = SubjectiveAnswer.objects.filter(question=original_question, student=stu_exam.student).first()  # type: ignore
            
            # Debug information
            print(f"DEBUG: Student {stu_exam.student.username}, Question: {stu_question.question[:50]}...")
            print(f"DEBUG: Original question: {original_question}")
            print(f"DEBUG: Found SubjectiveAnswer: {subj_answer is not None}")
            if subj_answer:
                print(f"DEBUG: Answer content: {subj_answer.text_answer or subj_answer.ocr_text}")
            
            answers.append({
                'question': stu_question.question,
                'subjective_answer': subj_answer,
            })
        student_data.append({
            'stu_exam': stu_exam,
            'answers': answers,
        })

    return render(request, 'prof/exam/evaluate_exam.html', {
        'exam': exam,
        'student_data': student_data,
        'prof': prof,
    })
