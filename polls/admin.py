from django.contrib import admin
from .models import Question, Choice
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


