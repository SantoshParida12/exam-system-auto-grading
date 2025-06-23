from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from main.models import *
from django.contrib.auth.models import User
from student.models import *
from django.utils import timezone
from ..forms import SubjectiveAnswerForm
from ..models import SubjectiveAnswer
from main.models import Question_DB
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from main.models.group import Special_Students
from ..utils import validate_image_file, extract_text_from_image, grade_answer, get_reference_answers_for_question


def exams(request):
    student = request.user

    studentGroup = Special_Students.objects.filter(students=student)  # type: ignore
    studentExamsList = StuExam_DB.objects.filter(student=student)  # type: ignore

    if request.method == 'POST' and not request.POST.get('papertitle', False):
        paper = request.POST['paper']
        print(f"Attempting exam: {paper}")  # Debug print
        
        try:
            stuExam = StuExam_DB.objects.get(examname=paper, student=student)  # type: ignore
            qPaper = stuExam.qpaper
            examMain = Exam_Model.objects.get(name=paper)  # type: ignore

            # TIME COMPARISON - Temporarily disabled for testing
            exam_start_time = examMain.start_time
            curr_time = timezone.now()
            
            print(f"Current time: {curr_time}")
            print(f"Exam start time: {exam_start_time}")
            print(f"Time difference: {curr_time - exam_start_time}")

            # Temporarily comment out timing check for testing
            # if curr_time < exam_start_time:
            #     print("Exam hasn't started yet")
            #     return redirect('student:exams')

            print("Starting exam...")
            
            # Reset exam completion status for new attempt
            stuExam.completed = 0
            stuExam.score = 0
            stuExam.save()
            print(f"Reset exam {paper} completion status for new attempt")
            
            # Clear any existing questions for this exam attempt
            stuExam.questions.all().delete()

            qPaperQuestionsList = qPaper.questions.all()
            print(f"Found {qPaperQuestionsList.count()} questions")
            
            for ques in qPaperQuestionsList:
                student_question = Stu_Question(question=ques.question, student=student, original_question=ques)
                student_question.save()
                stuExam.questions.add(student_question)
                stuExam.save()

            # Don't mark as completed yet - only when they submit
            # stuExam.completed = 1  # REMOVED - will be set when they submit
            stuExam.save()
            mins = examMain.duration
            secs = 0

            print("Rendering exam paper...")
            return render(request, 'student/paper/viewpaper.html', {
                'qpaper': qPaper, 'question_list': stuExam.questions.all(), 'student': student, 'exam': paper, 'min': mins, 'sec': secs
            })
            
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, f"Error starting exam: {e}")
            return redirect('student:exams')

    elif request.method == 'POST' and request.POST.get('papertitle', False):
        paper = request.POST['paper']
        title = request.POST['papertitle']
        stuExam = StuExam_DB.objects.get(examname=paper, student=student)  # type: ignore
        qPaper = stuExam.qpaper

        # Check if student actually submitted answers
        submitted_answers = False
        print(f"Processing exam submission for {paper}")
        print(f"Total questions: {stuExam.questions.count()}")
        
        for question in stuExam.questions.all():
            answer_text = request.POST.get(question.question, '').strip()
            image_file = request.FILES.get(f'image_{question.pk}', None)
            
            print(f"Question {question.pk}:")
            print(f"  - Text answer: '{answer_text}'")
            print(f"  - Image file: {image_file}")
            
            if answer_text or image_file:  # If any question has an answer
                submitted_answers = True
                print(f"[DEBUG] Question {question.pk}: Detected answer. Text: {bool(answer_text)}, Image: {bool(image_file)}")
                
                # Get the original question object from the original_question field
                original_question = question.original_question
                if not original_question:
                    original_question = question.question
                print(f"[DEBUG] Using original_question: {original_question}")
                
                try:
                    # Save answer to SubjectiveAnswer
                    subj_answer, created = SubjectiveAnswer.objects.get_or_create( #type: ignore
                        question=original_question,
                        student=student,
                        defaults={'marks': 0, 'feedback': 'Answer submitted, pending grading.'}
                    )
                    print(f"[DEBUG] SubjectiveAnswer {'created' if created else 'fetched'} for student {student.username}, question {original_question}")
                    # Prefer text answer if both are present
                    if answer_text:
                        subj_answer.text_answer = answer_text
                        subj_answer.image_answer = None
                        subj_answer.ocr_text = None
                        print(f"[DEBUG] Saved text answer.")
                    elif image_file:
                        print(f"[DEBUG] Received image file: {image_file}")
                        # Validate and process image
                        is_valid, error_msg = validate_image_file(image_file)
                        print(f"[DEBUG] Image validation: {is_valid}, {error_msg}")
                        if is_valid:
                            subj_answer.image_answer = image_file
                            subj_answer.text_answer = None
                            # Extract OCR text
                            ocr_text, ocr_error = extract_text_from_image(image_file)
                            print(f"[DEBUG] OCR result: '{ocr_text}', Error: {ocr_error}")
                            if ocr_text:
                                subj_answer.ocr_text = ocr_text
                                print(f"[DEBUG] Saved OCR text.")
                            elif ocr_error:
                                subj_answer.ocr_text = "OCR processing failed. Please check image quality."
                                print(f"[DEBUG] OCR failed: {ocr_error}")
                        else:
                            messages.error(request, f"Image error for question {question.pk}: {error_msg}")
                            print(f"[DEBUG] Image validation failed: {error_msg}")
                    subj_answer.save()
                    print(f"[DEBUG] SubjectiveAnswer saved for student {student.username}, question {original_question}")
                except Exception as e:
                    print(f"[DEBUG] Error creating SubjectiveAnswer: {e}")
                    messages.error(request, f"Error saving answer for question {question.pk}: {e}")
            else:
                print(f"  - No answer provided")
        
        print(f"Submitted answers detected: {submitted_answers}")
        
        if submitted_answers:
            # Student submitted answers - grade them using TF-IDF
            total_score = 0
            graded_questions = 0
            
            for question in stuExam.questions.all():
                # Get student's answer for this question
                original_question = question.original_question
                if not original_question:
                    original_question = question.question
                    
                student_answer = SubjectiveAnswer.objects.filter( #type: ignore
                    question=original_question,
                    student=student
                ).first()
                
                if student_answer:
                    # Get reference answers for this question
                    reference_answers = get_reference_answers_for_question(original_question)
                    
                    if reference_answers:
                        # Grade the answer using TF-IDF
                        score, feedback, best_reference = grade_answer(student_answer, reference_answers)
                        total_score += score
                        graded_questions += 1
                        
                        # Store the grade and feedback
                        student_answer.marks = score
                        student_answer.feedback = feedback
                        student_answer.save()
                        
                        print(f"Question {question.pk}: Score = {score:.1f}%, Feedback = {feedback}")
                    else:
                        print(f"No reference answers found for question {question.pk}")
            
            # Calculate total marks
            if graded_questions > 0:
                total_marks = total_score  # sum of marks for all questions
                stuExam.score = int(total_marks)
                print(f"Total marks: {total_marks} (out of {graded_questions * 5})")
            else:
                stuExam.score = 0
                print("No questions were graded")
            
            # Mark as completed
            stuExam.completed = 1
            stuExam.save()
            print(f"Exam {paper} marked as completed with total marks: {stuExam.score}")
        else:
            # Student didn't submit any answers - keep as incomplete
            stuExam.completed = 0
            stuExam.save()
            print(f"Exam {paper} kept as incomplete - no answers submitted")
            messages.warning(request, "No answers were submitted. The exam remains incomplete.")

        return render(request, 'student/result/result.html', {
            'Title': title, 'Score': f'{stuExam.score}' if submitted_answers else 'Incomplete', 'student': student
        })

    return render(request, 'student/exam/viewexam.html', {
        'student': student, 'paper': studentExamsList
    })

@login_required
def submit_subjective_answer(request, question_id):
    question = get_object_or_404(Question_DB, pk=question_id)
    # Prevent duplicate submissions
    existing = SubjectiveAnswer.objects.filter(question=question, student=request.user).first()  # type: ignore
    if existing:
        messages.info(request, "You have already submitted an answer for this question.")
        return redirect('student:view_answer', answer_id=existing.id)

    if request.method == 'POST':
        form = SubjectiveAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.student = request.user
            answer.question = question
            
            # Save OCR text if image was uploaded
            if form.cleaned_data.get('ocr_text'):
                answer.ocr_text = form.cleaned_data['ocr_text']
            
            answer.save()
            messages.success(request, "Your answer has been submitted successfully!")
            return redirect('student:exams')
    else:
        form = SubjectiveAnswerForm()
    return render(request, 'student/submit_subjective_answer.html', {
        'form': form,
        'question': question,
    })

@login_required
def view_answer(request, answer_id):
    answer = get_object_or_404(SubjectiveAnswer, id=answer_id, student=request.user)  # type: ignore
    return render(request, 'student/view_subjective_answer.html', {'answer': answer})
