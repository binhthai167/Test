from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Choice, Question
from django.shortcuts import render, redirect
from .models import ExamResult
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
import random
from .models import ExamCode
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .scoreforquestion import score_open_ended_answer

from .google_sheets import append_exam_result
from django.utils import timezone


def home(request):
    exam_date = request.session.get('exam_date')
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # Nếu qua ngày mới => reset toàn bộ session
    if exam_date and exam_date != today_str:
        request.session.flush()  
        request.session.clear_expired()
        
    entrance_exam_code = None
    post_training_exam_code = None

    # Mã bài sau đào tạo cố định
    FIXED_POST_TRAINING_CODE = "SAU_DAO_TAO_01" 
    
    all_codes = list(ExamCode.objects.values_list('code', flat=True))
    
    # --- THÊM PHẦN NÀY: Biến kiểm tra trạng thái hoàn thành ---
    entrance_completed = False
    post_training_completed = request.session.get(f'completed_{FIXED_POST_TRAINING_CODE}', False)

    if all_codes:
        entrance_codes = [code for code in all_codes if code != FIXED_POST_TRAINING_CODE]
        
        # Quét xem công nhân đã làm bất kỳ đề Đầu vào nào chưa
        for code in entrance_codes:
            if request.session.get(f'completed_{code}'):
                entrance_completed = True
                break

        if entrance_codes:
            entrance_exam_code = random.choice(entrance_codes)
            
        if FIXED_POST_TRAINING_CODE in all_codes:
            post_training_exam_code = FIXED_POST_TRAINING_CODE

    return render(request, 'polls/home.html', {
        'entrance_exam_code': entrance_exam_code,
        'post_training_exam_code': post_training_exam_code,
        'entrance_completed': entrance_completed,          # Truyền ra HTML
        'post_training_completed': post_training_completed # Truyền ra HTML
    })

def save_userInfo(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        request.session['username'] = username
        request.session['email'] = email
        if email and ExamResult.objects.filter(email=email).exists():
            exam_result = ExamResult.objects.get(email=email)
            request.session['exam_results'] = exam_result.results
            request.session['score'] = exam_result.score
            request.session['username'] = exam_result.username
            request.session['email'] = email
            request.session['passed'] = exam_result.passed
            return redirect('polls:result')
        
        return redirect('polls:index')
    return redirect('polls:home')

def start_exam(request, exam_code):
    today_str = datetime.now().strftime('%Y-%m-%d')
    exam_date = request.session.get('exam_date')

    # SỬA Ở ĐÂY: Kiểm tra hoàn thành theo từng mã đề (completed_ + mã đề)
    if request.session.get(f'completed_{exam_code}') and exam_date == today_str:
        return redirect('polls:result', exam_code=exam_code)
        
    exam_code_obj = get_object_or_404(ExamCode, code=exam_code)
    # Đã sửa order_by('question_text') thành order_by('id')
    questions = exam_code_obj.questions.all().order_by('id')
    return render(request, 'polls/index.html', {
        'exam_code': exam_code_obj,
        'questions': questions,
    })

def save_choice(request):
    if request.method == 'POST':
        q_id = request.POST.get('question_id')
        c_id = request.POST.get('choice_id')
        
        if q_id and c_id: 
            selected = request.session.get('selected_choices', {})
            selected[q_id] = c_id 
            request.session['selected_choices'] = selected
            request.session.modified = True
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)

@csrf_exempt
def save_text_answer(request):
    if request.method == 'POST':
        q_id = request.POST.get('question_id')
        answer_text = request.POST.get('answer_text', '').strip()
        
        if q_id is not None:
            try:
                question = Question.objects.get(pk=q_id)
                if question.question_type != 'TEXT':
                    return JsonResponse({'status': 'error', 'message': 'Câu hỏi không phải loại văn bản'}, status=400)
                
                text_answers = request.session.get('text_answers', {})
                text_answers[q_id] = answer_text
                request.session['text_answers'] = text_answers
                request.session.modified = True
                return JsonResponse({'status': 'ok', 'saved_answer': answer_text})
            except Question.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Câu hỏi không tồn tại'}, status=400)
        return JsonResponse({'status': 'error', 'message': 'Thiếu question_id'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Phương thức không hợp lệ'}, status=400)

@never_cache
def index(request, exam_code):
    today_str = datetime.now().strftime('%Y-%m-%d')
    exam_date = request.session.get('exam_date')
    
    # SỬA Ở ĐÂY: Lưu ý check đúng mã đề
    is_completed = request.session.get(f'completed_{exam_code}', False)
    
    if is_completed and exam_date == today_str:
        return redirect('polls:result', exam_code=exam_code)
        
    selected_choices = request.session.get('selected_choices', {})
    text_answers = request.session.get('text_answers', {})
    exam_code_obj = get_object_or_404(ExamCode, code=exam_code)
    # Đã thêm order_by('id') để sắp xếp đúng thứ tự
    questions = exam_code_obj.questions.all().order_by('id')
    
    if not questions:
        return render(request, 'polls/index.html', {
            'questions': [],
            'selected_choices': selected_choices,
            'text_answers': text_answers,
            'exam_completed': is_completed,
            'error_message': 'Không có câu hỏi nào được tìm thấy.',
            'exam_code': exam_code_obj, 
        })

    response = render(request, 'polls/index.html', {
        'questions': questions,
        'selected_choices': selected_choices,
        'text_answers': text_answers,
        'exam_completed': is_completed, 
        'exam_code': exam_code_obj, 
    })

    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@never_cache
def submit_exam(request, exam_code):
    exam_code_obj = get_object_or_404(ExamCode, code=exam_code)
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        supplier_company = request.POST.get('supplier_company', '').strip()
        license_plate = request.POST.get('license_plate', '').strip()
        
        # Lấy thêm Mã Nhân Viên (chỉ dành cho bài Sau đào tạo)
        employee_id = request.POST.get('employee_id', '').strip()
        
        # --- TÁCH KIỂM TRA LỖI LÀM 2 TRƯỜNG HỢP ---
        if exam_code == 'SAU_DAO_TAO_01':
            # 1. Bài sau đào tạo: Bắt buộc có Họ tên và Mã NV
            if not username or not employee_id:
                return render(request, 'polls/index.html', {
                    # Đã sửa thành order_by('id')
                    'questions': exam_code_obj.questions.all().order_by('id'),
                    'selected_choices': request.session.get('selected_choices', {}),
                    'text_answers': request.session.get('text_answers', {}),
                    'error_message': 'Vui lòng nhập Họ tên và Mã số nhân viên.',
                    'exam_code': exam_code_obj
                })
            # Biến tấu dữ liệu để qua được bước lưu Database (sẽ không đẩy cái này lên Google Sheets)
            phone = employee_id
            email = f"{employee_id}@noemail.com"  
            supplier_company = "Nội bộ"
            request.session['employee_id'] = employee_id
            
        else:
            # 2. Bài Đầu vào: Bắt buộc có Họ tên và Email
            if not username or not email:
                return render(request, 'polls/index.html', {
                    # Đã sửa thành order_by('id')
                    'questions': exam_code_obj.questions.all().order_by('id'),
                    'selected_choices': request.session.get('selected_choices', {}),
                    'text_answers': request.session.get('text_answers', {}),
                    'error_message': 'Vui lòng nhập đầy đủ tên và email.',
                    'exam_code': exam_code_obj 
                })

        # --- BẮT ĐẦU TÍNH ĐIỂM ---
        # Đã sửa thành order_by('id')
        questions = exam_code_obj.questions.all().order_by('id')
        score = 0
        results = []
        for question in questions:
            field_name = f'question_{question.id}'
            if question.question_type == 'TEXT':
                answer_text = request.POST.get(field_name, '').strip()
                
                # Ném hết sang file scoreforquestion.py để chấm
                text_score = score_open_ended_answer(answer_text, question, exam_code)
                score += text_score
                is_correct = (text_score == question.max_score)

                results.append({
                    'exam_code': exam_code,
                    'question': question.question_text,
                    'selected': answer_text if answer_text else 'x',
                    'correct_answer': question.correct_answer,
                    'question_type': 'TEXT',
                    'is_correct': is_correct
                })
            else: 
                selected_choice_id = request.POST.get(field_name)
                try:
                    selected_choice = Choice.objects.get(pk=selected_choice_id)
                    is_correct = selected_choice.is_correct
                    if is_correct:
                        score += question.max_score
                    results.append({
                        'exam_code': exam_code,
                        'question': question.question_text,
                        'selected': selected_choice.choice_text,
                        'is_correct': is_correct
                    })
                except Choice.DoesNotExist:
                    results.append({
                        'exam_code': exam_code,
                        'question': question.question_text,
                        'selected': 'Không chọn',
                        'is_correct': False
                    })
        
        score = round(score, 1) 
        passed = score >= 5
        try:
            # Lưu vào Database với dữ liệu giả để không bị crash
            ExamResult.objects.create(
                username=username,
                email=email,
                phone=phone,
                supplier_company=supplier_company,
                license_plate=license_plate,
                score=score,
                passed=passed,
                results=results
            )
            
            # --- ĐẨY LÊN GOOGLE SHEETS ---
            submitted_at = timezone.localtime(timezone.now()).strftime("%d-%m-%Y")
            
            # Phân tách dữ liệu đẩy lên Sheet tùy theo loại bài
            if exam_code == 'SAU_DAO_TAO_01':
                # Bài Sau đào tạo: Cột SDT gán bằng employee_id, bỏ hẳn Email, Công ty, Biển số
                row_data = [
                    submitted_at, 
                    username, 
                    employee_id,  
                    score,        
                    "Đậu" if passed else "Rớt",
                ]
            else:
                # Bài Đầu vào: Đẩy đầy đủ thông tin bình thường
                row_data = [
                    submitted_at, 
                    username, 
                    phone, 
                    email, 
                    supplier_company, 
                    license_plate, 
                    score, 
                    "Đậu" if passed else "Rớt",
                ]    
            
            # Thêm các câu trả lời vào row_data
            for r in results:
                row_data.append(r['selected'])  
            
            # Gửi vào Sheet Đầu ra / Đầu vào
            if exam_code == 'SAU_DAO_TAO_01':
                target_sheet = "Đầu ra"
            else:
                target_sheet = "Đầu vào"
            append_exam_result(row_data, target_sheet)
          
        except IntegrityError:
            return redirect('polls:result', exam_code=exam_code)
            
        request.session[f'completed_{exam_code}'] = True 
        request.session['exam_date'] = datetime.now().strftime('%Y-%m-%d')
        request.session['email'] = email
        request.session['username'] = username
        request.session.modified = True
        return redirect('polls:result', exam_code=exam_code)
    
    return redirect('polls:index', exam_code=exam_code)

@never_cache
def result(request, exam_code):
    email = request.session.get('email', '')
    results = []         
    score = 0
    username = 'Người dùng'
    passed = False
    
    if email:
        exam_result = (
            ExamResult.objects.filter(email=email)
            .order_by('-submit_time')  
            .first()
        )
        if exam_result:
            results = exam_result.results
            score = round(exam_result.score, 1)
            username = exam_result.username
            passed = exam_result.passed
       
    filtered_results = [
        r for r in results if str(r.get('exam_code')) == str(exam_code)
    ]

    return render(request, 'polls/result.html', {
        'score': score,
        'results': filtered_results, 
        'username': username,
        'passed': passed
    })

def loaderio_verification(request):
    return HttpResponse("loaderio-d62c75f95bb592331c05c414e7ba073a", content_type="text/plain")