from django.urls import path
from . import views

urlpatterns = [
    path('question/', views.add_question, name='add_question'),
    path('question/multiple/', views.add_multiple_questions, name='add_multiple_questions'),
    path('question/view_all_ques/', views.view_all_ques, name='view_all_ques'),
    path('question/edit_question/<int:ques_qno>/', views.edit_question, name='edit_question'),
]