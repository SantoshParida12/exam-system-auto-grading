from django.urls import path, include
from . import views
from student.views.exams import submit_subjective_answer, view_answer

app_name = 'student'

urlpatterns = [
                                # HOME
    path('', views.index, name='index'),
    
                                # EXAM
    path('exams/', views.exams, name='exams'),
    path('results/', views.results, name='results'),
    path('submit_answer/<int:question_id>/', submit_subjective_answer, name='submit_subjective_answer'),
    path('view_answer/<int:answer_id>/', view_answer, name='view_answer'),

    path('api/', include('student.api.urls')),
]
