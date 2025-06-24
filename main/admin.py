from django.contrib import admin
from .models import *
from .models.reference_answer import ReferenceAnswer
from .models.question import Question_DB

# Register your models here.

class QuestionDBAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False  # Disables delete for all users

admin.site.register(Question_DB, QuestionDBAdmin)

admin.site.register(Question_Paper)
admin.site.register(Special_Students)
admin.site.register(Exam_Model)

@admin.register(ReferenceAnswer)
class ReferenceAnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'professor', 'has_text_answer', 'has_image_answer', 'has_ocr_text', 'created_at']
    list_filter = ['professor', 'created_at']
    search_fields = ['question__question', 'professor__username']
    readonly_fields = ['ocr_text', 'tfidf_vector', 'created_at', 'updated_at']
    
    def has_text_answer(self, obj):
        return bool(obj.text_answer)
    has_text_answer.boolean = True
    has_text_answer.short_description = 'Text Answer'
    
    def has_image_answer(self, obj):
        return bool(obj.image_answer)
    has_image_answer.boolean = True
    has_image_answer.short_description = 'Image Answer'
    
    def has_ocr_text(self, obj):
        return bool(obj.ocr_text)
    has_ocr_text.boolean = True
    has_ocr_text.short_description = 'OCR Text'
    
    fieldsets = (
        ('Question Information', {
            'fields': ('question', 'professor')
        }),
        ('Answer Content', {
            'fields': ('text_answer', 'image_answer')
        }),
        ('OCR & Analysis', {
            'fields': ('ocr_text', 'tfidf_vector'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )