from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from django.contrib.auth.models import User
from main.models.exam import Exam_Model
from student.models import ExamResults, StuExam_DB, SubjectiveAnswer
from prof.views.exam import evaluate_exam


def view_all_results(request):
    """
    Display all exam results for the professor's exams
    """
    prof = request.user
    
    # Get all exams created by this professor
    exams = Exam_Model.objects.filter(professor=prof).order_by('-start_time')
    
    # Get statistics for each exam
    exam_stats = []
    for exam in exams:
        # Get all results for this exam
        results = ExamResults.objects.filter(exam=exam)
        
        # Calculate statistics
        total_students = results.count()
        completed_students = results.filter(is_completed=True).count()
        passed_students = results.filter(is_passed=True).count()
        average_score = results.filter(is_completed=True).aggregate(Avg('percentage'))['percentage__avg'] or 0
        
        exam_stats.append({
            'exam': exam,
            'total_students': total_students,
            'completed_students': completed_students,
            'passed_students': passed_students,
            'average_score': round(average_score, 2),
            'completion_rate': round((completed_students / total_students * 100) if total_students > 0 else 0, 2),
            'pass_rate': round((passed_students / completed_students * 100) if completed_students > 0 else 0, 2),
        })
    
    return render(request, 'prof/results/all_results.html', {
        'prof': prof,
        'exam_stats': exam_stats,
    })


def view_exam_results(request, exam_id):
    """
    Display detailed results for a specific exam
    """
    prof = request.user
    exam = Exam_Model.objects.get(professor=prof, pk=exam_id)
    
    # Get all results for this exam
    results = ExamResults.objects.filter(exam=exam).order_by('-percentage', '-completed_at')
    
    # Calculate overall statistics
    total_students = results.count()
    completed_students = results.filter(is_completed=True).count()
    passed_students = results.filter(is_passed=True).count()
    
    # Score distribution
    score_ranges = {
        'A+ (90-100%)': results.filter(percentage__gte=90).count(),
        'A (80-89%)': results.filter(percentage__gte=80, percentage__lt=90).count(),
        'B+ (70-79%)': results.filter(percentage__gte=70, percentage__lt=80).count(),
        'B (60-69%)': results.filter(percentage__gte=60, percentage__lt=70).count(),
        'C+ (50-59%)': results.filter(percentage__gte=50, percentage__lt=60).count(),
        'C (40-49%)': results.filter(percentage__gte=40, percentage__lt=50).count(),
        'D (30-39%)': results.filter(percentage__gte=30, percentage__lt=40).count(),
        'F (0-29%)': results.filter(percentage__lt=30).count(),
    }
    
    # Average statistics
    avg_stats = results.filter(is_completed=True).aggregate(
        avg_percentage=Avg('percentage'),
        avg_completion_rate=Avg('completion_rate'),
        avg_accuracy_rate=Avg('accuracy_rate'),
    )
    
    return render(request, 'prof/results/exam_results.html', {
        'prof': prof,
        'exam': exam,
        'results': results,
        'total_students': total_students,
        'completed_students': completed_students,
        'passed_students': passed_students,
        'completion_rate': round((completed_students / total_students * 100) if total_students > 0 else 0, 2),
        'pass_rate': round((passed_students / completed_students * 100) if completed_students > 0 else 0, 2),
        'score_ranges': score_ranges,
        'avg_stats': avg_stats,
    })


def view_student_results(request, exam_id, student_id):
    """
    Display detailed results for a specific student's exam
    """
    prof = request.user
    exam = Exam_Model.objects.get(professor=prof, pk=exam_id)
    student = User.objects.get(pk=student_id)
    
    # Get the exam result
    try:
        exam_result = ExamResults.objects.get(exam=exam, student=student)
    except ExamResults.DoesNotExist:
        messages.error(request, "No results found for this student.")
        return redirect('prof:view_exam_results', exam_id=exam_id)
    
    # Get all subjective answers for this exam
    student_exam = exam_result.student_exam
    answers = []
    
    for question in student_exam.questions.all():
        original_question = question.original_question
        if not original_question:
            original_question = question.question
            
        answer = SubjectiveAnswer.objects.filter(
            question=original_question,
            student=student
        ).first()
        
        answers.append({
            'question': question,
            'answer': answer,
        })
    
    return render(request, 'prof/results/student_results.html', {
        'prof': prof,
        'exam': exam,
        'student': student,
        'exam_result': exam_result,
        'answers': answers,
    })


def export_results(request, exam_id):
    """
    Export exam results to CSV
    """
    prof = request.user
    exam = Exam_Model.objects.get(professor=prof, pk=exam_id)
    
    import csv
    from django.http import HttpResponse
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{exam.name}_results.csv"'
    
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Student ID', 'Student Name', 'Email', 'Total Questions', 
        'Questions Attempted', 'Questions Correct', 'Questions Partial', 
        'Questions Incorrect', 'Total Score', 'Max Possible Score', 
        'Percentage', 'Grade', 'Completion Rate', 'Accuracy Rate', 
        'Time Taken', 'Completed At', 'Passed'
    ])
    
    # Get all results for this exam
    results = ExamResults.objects.filter(exam=exam).order_by('-percentage')
    
    # Write data rows
    for result in results:
        writer.writerow([
            result.student.id,
            result.student.username,
            result.student.email,
            result.total_questions,
            result.questions_attempted,
            result.questions_correct,
            result.questions_partial,
            result.questions_incorrect,
            result.total_score,
            result.max_possible_score,
            f"{result.percentage:.2f}%",
            result.grade_letter,
            f"{result.completion_rate:.2f}%",
            f"{result.accuracy_rate:.2f}%",
            str(result.time_taken) if result.time_taken else 'N/A',
            result.completed_at.strftime('%Y-%m-%d %H:%M:%S') if result.completed_at else 'N/A',
            'Yes' if result.is_passed else 'No'
        ])
    
    return response


def results_analytics(request, exam_id):
    """
    Display analytics and charts for exam results
    """
    prof = request.user
    exam = Exam_Model.objects.get(professor=prof, pk=exam_id)
    
    # Get all results for this exam
    results = ExamResults.objects.filter(exam=exam, is_completed=True)
    
    # Prepare data for charts
    chart_data = {
        'score_distribution': {
            'labels': ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F'],
            'data': [
                results.filter(percentage__gte=90).count(),
                results.filter(percentage__gte=80, percentage__lt=90).count(),
                results.filter(percentage__gte=70, percentage__lt=80).count(),
                results.filter(percentage__gte=60, percentage__lt=70).count(),
                results.filter(percentage__gte=50, percentage__lt=60).count(),
                results.filter(percentage__gte=40, percentage__lt=50).count(),
                results.filter(percentage__gte=30, percentage__lt=40).count(),
                results.filter(percentage__lt=30).count(),
            ]
        },
        'completion_vs_accuracy': {
            'completion_rates': [r.completion_rate for r in results],
            'accuracy_rates': [r.accuracy_rate for r in results],
        }
    }
    
    return render(request, 'prof/results/results_analytics.html', {
        'prof': prof,
        'exam': exam,
        'chart_data': chart_data,
        'total_students': results.count(),
    })


def update_manual_grade(request, answer_id):
    """
    Update manual grade for a subjective answer
    """
    if request.method == 'POST':
        try:
            answer = SubjectiveAnswer.objects.get(pk=answer_id)
            new_marks = int(request.POST.get('marks', 0))
            teacher_feedback = request.POST.get('teacher_feedback', '')
            
            # Update the answer
            answer.marks = new_marks
            answer.teacher_feedback = teacher_feedback
            answer.is_teacher_graded = True
            answer.graded_by = request.user
            answer.save()
            
            # Recalculate exam results
            exam_result = ExamResults.objects.get(student=answer.student, student_exam__questions__original_question=answer.question)
            exam_result.save()  # This will trigger recalculation
            
            return JsonResponse({'success': True, 'message': 'Grade updated successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
