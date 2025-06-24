from django.contrib import admin
from .models import *

# Register your models here.
# admin.site.register(Stu_Question)  # Hide per-student questions from admin
admin.site.register(StuExam_DB)
admin.site.register(StuResults_DB)