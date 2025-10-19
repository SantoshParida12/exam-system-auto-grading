from django.shortcuts import render, redirect
from main.models import *
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.contrib import messages


def add_question(request):
    prof = request.user

    if request.method == 'POST':
        form = QForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.professor = prof
            print(f"[DEBUG] Creating question: '{form.question[:60]}' by professor: {prof.username if prof else 'None'}")
            form.save()
            print(f"[DEBUG] Saved question with qno: {form.qno}, professor: {form.professor.username if form.professor else 'None'}")
            messages.success(request, 'Question created successfully!')
            return redirect('prof:view_all_ques')

    return render(request, 'prof/question/question.html', {
        'question_db': Question_DB.objects.filter(professor=prof), 'form': QForm(), 'prof': prof  # type: ignore
    })


def add_multiple_questions(request):
    prof = request.user

    if request.method == 'POST':
        questions_text = request.POST.get('questions_text', '').strip()
        
        if questions_text:
            # Split questions by new lines or numbered format
            questions = []
            lines = questions_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line:
                    # Remove question numbers if present (e.g., "1.", "Q1.", etc.)
                    import re
                    line = re.sub(r'^(\d+\.|Q\d+\.|Question\s*\d+\.?)\s*', '', line, flags=re.IGNORECASE)
                    if line:
                        questions.append(line)
            
            if questions:
                created_count = 0
                for question_text in questions:
                    if len(question_text) > 10:  # Minimum question length
                        print(f"[DEBUG] Creating question: '{question_text[:60]}' by professor: {prof.username if prof else 'None'}")
                        q = Question_DB.objects.create(  # type: ignore
                            professor=prof,
                            question=question_text,
                            question_type='SUBJECTIVE'
                        )
                        print(f"[DEBUG] Saved question with qno: {q.qno}, professor: {q.professor.username if q.professor else 'None'}")
                        created_count += 1
                
                if created_count > 0:
                    messages.success(request, f'{created_count} questions created successfully!')
                else:
                    messages.warning(request, 'No valid questions found. Please check your input.')
            else:
                messages.error(request, 'Please enter at least one question.')
        else:
            messages.error(request, 'Please enter questions text.')

    return render(request, 'prof/question/add_multiple_questions.html', {
        'prof': prof
    })

   
def view_all_ques(request):
    prof = request.user

    if request.method == 'POST':
        qno_raw = (request.POST.get('qno') or '').strip()
        try:
            Q_No = int(qno_raw)
        except ValueError:
            messages.error(request, 'Invalid question number.')
            return redirect('prof:view_all_ques')

        # Ensure the target question exists
        target = Question_DB.objects.filter(professor=prof, qno=Q_No).first()  # type: ignore
        if not target:
            messages.error(request, 'Question not found.')
            return redirect('prof:view_all_ques')

        # Delete selected question (use queryset delete to avoid custom delete guard)
        Question_DB.objects.filter(professor=prof, qno=Q_No).delete()  # type: ignore
        messages.success(request, f'Question #{Q_No} deleted successfully.')

    # Ensure any legacy questions without owner are assigned to this professor (single-professor setup)
    Question_DB.objects.filter(professor__isnull=True).update(professor=prof)  # type: ignore

    return render(request, 'prof/question/view_all_questions.html', {
        'question_db': Question_DB.objects.filter(professor=prof), 'prof': prof  # type: ignore
    })

    
def edit_question(request, ques_qno):
    prof = request.user
    ques = Question_DB.objects.get(professor=prof, qno=ques_qno)  # type: ignore
    form = QForm(instance=ques)

    if request.method == "POST":
        form = QForm(request.POST, instance=ques)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('prof:view_all_ques')

    return render(request, 'prof/question/edit_question.html', {
        'i': Question_DB.objects.filter(professor=prof, qno=ques_qno).first(), 'form': form, 'prof': prof  # type: ignore
    })
