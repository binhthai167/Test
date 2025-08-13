from django.contrib import admin
from import_export.admin import ImportExportModelAdmin  # Thêm dòng này
from .models import Question, Choice, ExamResult, ExamCode
from django.utils.html import format_html
from import_export import resources, fields
from .models import ExamResult
import json
# Register your models here.

class ChoiceInline(admin.TabularInline):    
    model = Choice
    extra = 4
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('question_text', 'question_type', 'max_score'),
            'description': 'Nhập thông tin cơ bản của câu hỏi.'
        }),
        ('Câu hỏi tự luận', {
            'fields': ('correct_answer', 'keywords'),
            'description': (
                'Nhập <strong>Đáp án chính xác</strong> cho câu hỏi có đáp án cố định (ví dụ: toán học). '
                'Để trống nếu là câu hỏi mở.<br>'
                'Nhập <strong>Từ khóa</strong> cho câu hỏi mở, cách nhau bởi dấu phẩy (ví dụ: dự án, đội nhóm, kỹ năng). '
                'Để trống nếu không cần từ khóa.'
            ),
        }),
    )
    inlines = [ChoiceInline]
    list_display = ('question_text', 'question_type')
    list_filter = ('question_type',)
    def get_inline_instances(self, request, obj=None):
        """Ẩn ChoiceInline nếu là câu hỏi dạng TEXT."""
        if obj and obj.question_type == 'TEXT':
            return []
        return super().get_inline_instances(request, obj)
admin.site.register(Question, QuestionAdmin)
class ExamCodeAdmin(admin.ModelAdmin):
    list_display = ('code',)
    filter_horizontal = ('questions',)  # UI chọn nhiều câu hỏi
admin.site.register(ExamCode, ExamCodeAdmin)


class ExamResultResource(resources.ModelResource):
    formatted_results = fields.Field(column_name='Chi tiết kết quả')

    class Meta:
        model = ExamResult
        fields = ('username', 'email', 'score', 'passed', 'submit_time', 'formatted_results')

    def dehydrate_formatted_results(self, obj):
        if not obj.results:
            return "Chưa có dữ liệu kết quả."
        
        lines = []
        for r in obj.results:
            question = r.get('question', 'Không có câu hỏi')
            selected = r.get('selected', 'Không trả lời')
            q_type = r.get('question_type', 'CHOICE')
            is_correct = r.get('is_correct', None)

            if q_type == 'TEXT':
                lines.append(f"{question} | : {selected}")
            else:
                status = "✅" if is_correct else "❌"
                lines.append(f"{question} | Chọn: {selected} {status}")
        
        return "\n".join(lines) 

class ExamResultAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ExamResultResource
    list_display = ('username', 'email', 'score', 'passed', 'submit_time', )
    readonly_fields = ('formatted_results',)

    def formatted_results(self, obj):
        if not obj.results:
            return "Chưa có dữ liệu kết quả."
        
        html = "<ol>"
        for r in obj.results:
            question = r.get('question', 'Không có câu hỏi')
            selected = r.get('selected', 'Không trả lời')
            q_type = r.get('question_type', 'CHOICE')
            is_correct = r.get('is_correct', None)

            if q_type == 'TEXT':
                html += f"<li><strong>{question}</strong><br><em>Trả lời:</em> {selected}</li>"
            else:
                status = "✅" if is_correct else "❌"
                html += f"<li><strong>{question}</strong><br><em>Chọn:</em> {selected} {status}</li>"
        html += "</ol>"

        return format_html(html)

    formatted_results.short_description = "Chi tiết kết quả"

admin.site.register(ExamResult, ExamResultAdmin)

