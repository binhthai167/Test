from django.contrib import admin
from import_export.admin import ImportExportModelAdmin  # Thêm dòng này
from .models import Question, Choice, ExamResult, ExamCode
from django.utils.html import format_html
from import_export import resources, fields
from .models import ExamResult
from django.utils.timezone import localtime
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
    username = fields.Field(
        column_name='Họ và tên',
        attribute='username'
    )
    email = fields.Field(
        column_name='Email liên hệ',
        attribute='email'
    )
    phone = fields.Field(
        column_name='Số điện thoại',
        attribute='phone'
    )
    supplier_company = fields.Field(
        column_name='Công ty cung ứng',
        attribute='supplier_company'
    )
    license_plate = fields.Field(
        column_name='Biển số xe',
        attribute='license_plate'
    )
    score = fields.Field(
        column_name='Điểm',
        attribute='score'
    )
    passed = fields.Field(
        column_name='Kết quả',
        attribute='passed'
    )
    def dehydrate_passed(self, obj):
        return "Đạt" if obj.passed else "Không đạt"
    submit_time = fields.Field(
        column_name='Thời gian nộp',
        attribute='submit_time'
    )
    formatted_results = fields.Field(
        column_name='Chi tiết kết quả'
    )
    class Meta:
        model = ExamResult
        fields = (
            'username',
            'email',
            'phone',
            'supplier_company',
            'license_plate',
            'score',
            'passed',
            'submit_time',
            'formatted_results'
        )

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
    list_display = ('username_display', 'email_display', 'phone_display', 'supplier_company_display', 'license_plate_display', 'score_display', 'passed_display', 'submit_time_display', )
    list_filter = (
        'passed', 
        ('submit_time', admin.DateFieldListFilter),  # Filter theo ngày
    )
    readonly_fields = ('formatted_results',)
    date_hierarchy = 'submit_time'


    def username_display(self, obj):
        return obj.username or "Không có tên"
    username_display.short_description = 'Họ và tên'
    def email_display(self, obj):
        return obj.email or "Không có email"
    email_display.short_description = 'Email'
    def phone_display(self, obj):
        return obj.phone or "Không có số điện thoại"    
    phone_display.short_description = 'Số điện thoại'
    def supplier_company_display(self, obj):
        return obj.supplier_company or "Không có công ty"
    supplier_company_display.short_description = 'Công ty cung ứng'
    def license_plate_display(self, obj):
        return obj.license_plate or "Không có biển số xe"   
    license_plate_display.short_description = 'Biển số xe'
    def score_display(self, obj):
        return f"{obj.score:.1f}"
    score_display.short_description = 'Điểm'
    score_display.admin_order_field = 'score'  # Cho phép sắp xếp theo điểm
    def passed_display(self, obj):
        return "Đạt" if obj.passed else "Không đạt" 
    passed_display.short_description = 'Kết quả'
    passed_display.admin_order_field = 'passed'  # Cho phép sắp xếp theo kết quả
    def submit_time_display(self, obj):
        return localtime(obj.submit_time).strftime('%Y-%m-%d %H:%M:%S') if obj.submit_time else "Chưa có thời gian"
    submit_time_display.short_description = 'Thời gian nộp'
    submit_time_display.admin_order_field = 'submit_time'  # Cho phép sắp xếp theo thời gian nộp
    
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

