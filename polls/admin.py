from django.contrib import admin
from import_export.admin import ImportExportModelAdmin  # Thêm dòng này
from .models import Question, Choice, ExamResult
# Register your models here.

class ChoiceInline(admin.TabularInline):    
    model = Choice
    extra = 4
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),  
        
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text',)
    
admin.site.register(Question, QuestionAdmin)
class ExamResultAdmin(ImportExportModelAdmin):
    list_display = ('username', 'score', 'submit_time', 'passed')  # Thêm 'passed'
    list_filter = ('submit_time', 'passed')
    search_fields = ('username',)

admin.site.register(ExamResult, ExamResultAdmin)



