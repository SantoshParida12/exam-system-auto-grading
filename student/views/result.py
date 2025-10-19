from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.db import models
from main.models import *
from django.contrib.auth.models import User
from student.models import *
from student.utils import grade_answer, get_reference_answers_for_question


def results(request):
    student = request.user

    studentGroup = Special_Students.objects.filter(students=student) # type: ignore 
    studentExamList = StuExam_DB.objects.filter(student=student, completed=1) # type: ignore

    if request.method == 'POST':
        paper = request.POST['paper']
        viewExam = StuExam_DB.objects.get(examname=paper, student=student) # type: ignore
        
        # Auto-grade any ungraded answers when viewing results
        auto_grade_exam(viewExam, student)
        
        # Prepare questions with their answers for the template
        questions_with_answers = []
        for stu_question in viewExam.questions.all():
            original_question = stu_question.original_question
            if not original_question:
                original_question = stu_question.question
                
            student_answer = SubjectiveAnswer.objects.filter( # type: ignore
                question=original_question,
                student=student
            ).first()
            
            questions_with_answers.append({
                'question': stu_question,
                'answer': student_answer
            })
        
        return render(request, 'student/result/individualresult.html', {
            'exam': viewExam, 'student': student, 'questions_with_answers': questions_with_answers
        })

    # Aggregate stats for results overview
    completed_count = studentExamList.count()
    latest_exam = studentExamList.order_by('-completed_at', '-started_at').first()
    latest_score = latest_exam.score if latest_exam else 0
    # Compute average percentage across completed exams
    totals = studentExamList.aggregate(total_score=models.Sum('score'), total_max=models.Sum('total_marks_possible'))
    total_score_sum = totals.get('total_score') or 0
    total_max_sum = totals.get('total_max') or 0
    average_percentage = int(round((total_score_sum / total_max_sum) * 100)) if total_max_sum else 0

    def pct_to_grade(p):
        if p >= 90:
            return 'A+'
        if p >= 80:
            return 'A'
        if p >= 70:
            return 'B'
        if p >= 60:
            return 'C'
        return 'D'

    average_grade = pct_to_grade(average_percentage)
    success_rate = int(round((studentExamList.filter(score__gte=1).count() / completed_count) * 100)) if completed_count else 0

    return render(request, 'student/result/results.html', {
        'student': student,
        'paper': studentExamList,
        'completed_count': completed_count,
        'latest_score': latest_score,
        'average_grade': average_grade,
        'success_rate': success_rate,
    })


def auto_grade_exam(exam, student):
    """
    Automatically grade any ungraded answers in an exam
    """
    from student.models import SubjectiveAnswer
    
    print(f"Auto-grading exam {exam.examname} for student {student.username}")
    
    total_score = 0
    graded_questions = 0
    updated_answers = False
    
    for question in exam.questions.all():
        # Get student's answer for this question
        original_question = question.original_question
        if not original_question:
            original_question = question.question
            
        student_answer = SubjectiveAnswer.objects.filter( # type: ignore
            question=original_question,
            student=student
        ).first()
        
        if student_answer and (student_answer.marks == 0 or not student_answer.feedback):
            # Answer exists but not graded yet - try to grade it
            reference_answers = get_reference_answers_for_question(original_question)
            
            if reference_answers:
                # Grade the answer using TF-IDF
                score, feedback, best_reference = grade_answer(student_answer, reference_answers)
                
                # Update the answer with grade and feedback
                student_answer.marks = score
                student_answer.feedback = feedback
                student_answer.save()
                
                total_score += score
                graded_questions += 1
                updated_answers = True
                
                print(f"Auto-graded Question {question.pk}: Score = {score}/5, Feedback = {feedback}")
            else:
                # No reference answers - provide default feedback
                student_answer.marks = 0
                student_answer.feedback = "Answer submitted successfully. No reference answers available for automated grading."
                student_answer.save()
                
                updated_answers = True
                print(f"Question {question.pk}: No reference answers - provided default feedback")
        elif student_answer:
            # Answer already graded
            total_score += student_answer.marks
            graded_questions += 1
            print(f"Question {question.pk} already graded: {student_answer.marks}/5")
    
    # Update exam score if we graded any new answers
    if updated_answers and graded_questions > 0:
        exam.score = int(total_score)
        exam.save()
        print(f"Updated exam score to {total_score} (out of {graded_questions * 5})")
    
    return updated_answers