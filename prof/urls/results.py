from django.urls import path
from ..views.results import (
    view_all_results,
    view_exam_results, 
    view_student_results,
    export_results,
    results_analytics,
    update_manual_grade
)

urlpatterns = [
    # Results URLs
    path('results/', view_all_results, name='view_all_results'),
    path('results/exam/<int:exam_id>/', view_exam_results, name='view_exam_results'),
    path('results/exam/<int:exam_id>/student/<int:student_id>/', view_student_results, name='view_student_results'),
    path('results/exam/<int:exam_id>/export/', export_results, name='export_results'),
    path('results/exam/<int:exam_id>/analytics/', results_analytics, name='results_analytics'),
    path('results/update-grade/<int:answer_id>/', update_manual_grade, name='update_manual_grade'),
]
