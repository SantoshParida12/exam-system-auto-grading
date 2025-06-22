from django.urls import path
from . import results, exams, ocr

app_name = 'api'

urlpatterns = [
    path('results/<int:pk>', results.Results.as_view()),
    path('exams/<int:pk>', exams.Exam.as_view(), name='exams'),
    path('results', results.Results.as_view(), name='results'),
    path('ocr', ocr.OCRView.as_view(), name='ocr'),
]
