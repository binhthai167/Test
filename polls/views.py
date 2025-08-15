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


def home(request):
    exam_date = request.session.get('exam_date')
    today_str = datetime.now().strftime('%Y-%m-%d')
    # Nếu đã hoàn thành nhưng ngày làm khác hôm nay => reset
    if request.session.get('exam_completed') and exam_date != today_str:
        request.session.flush()  # Xóa toàn bộ session
        request.session.clear_expired()
    if request.session.get('exam_completed'):
        random_exam_code = None
    else:
        exam_codes = list(ExamCode.objects.values_list('code', flat=True))
        random_exam_code = random.choice(exam_codes) if exam_codes else None

    return render(request, 'polls/home.html', {
        'random_exam_code': random_exam_code
    })
def save_userInfo(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        request.session['username'] = username
        request.session['email'] = email
        if email and ExamResult.objects.filter(email=email).exists():
            exam_result = ExamResult.objects.get(email=email)
            # Khôi phục kết quả vào session
            request.session['exam_results'] = exam_result.results
            request.session['score'] = exam_result.score
            request.session['username'] = exam_result.username
            request.session['email'] = email
            request.session['passed'] = exam_result.passed
            request.session['exam_completed'] = True
            return redirect('polls:result')
        
        return redirect('polls:index')
    return redirect('polls:home')
def start_exam(request, exam_code):
    today_str = datetime.now().strftime('%Y-%m-%d')
    exam_date = request.session.get('exam_date')

    if request.session.get('exam_completed') and exam_date == today_str:
        return redirect('polls:result', exam_code=exam_code)
    exam_code_obj = get_object_or_404(ExamCode, code=exam_code)
    questions = exam_code_obj.questions.all().order_by('question_text')
    return render(request, 'polls/index.html', {
        'exam_code': exam_code_obj,   # Phải truyền biến exam_code_obj dưới tên exam_code
        'questions': questions,
    })
def save_choice(request):
    if request.method == 'POST':
        q_id = request.POST.get('question_id')
        c_id = request.POST.get('choice_id')
        
        if q_id and c_id:  # Kiểm tra dữ liệu hợp lệ
            selected = request.session.get('selected_choices', {})
            selected[q_id] = c_id  # Lưu trực tiếp, không cần chuyển thành chuỗi
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
                # print("Saved text_answers:", text_answers)  # Debug
                return JsonResponse({'status': 'ok', 'saved_answer': answer_text})
            except Question.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Câu hỏi không tồn tại'}, status=400)
        return JsonResponse({'status': 'error', 'message': 'Thiếu question_id'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Phương thức không hợp lệ'}, status=400)

@never_cache
def index(request, exam_code):
    if request.session.get('exam_completed', False):
        return redirect('polls:result')
    today_str = datetime.now().strftime('%Y-%m-%d')
    exam_date = request.session.get('exam_date')
    if request.session.get('exam_completed') and exam_date == today_str:
        return redirect('polls:result', exam_code=exam_code)
    # Khởi tạo session nếu chưa có
    selected_choices = request.session.get('selected_choices', {})
    text_answers = request.session.get('text_answers', {})
    exam_code_obj = get_object_or_404(ExamCode, code=exam_code)
    # Lấy danh sách câu hỏi
    questions = exam_code_obj.questions.all()
    if not questions:
        # Xử lý trường hợp không có câu hỏi
        return render(request, 'polls/index.html', {
            'questions': [],
            'selected_choices': selected_choices,
            'text_answers': text_answers,
            'exam_completed': False,
            'error_message': 'Không có câu hỏi nào được tìm thấy.',
            'exam_code': exam_code_obj,  # truyền object
        })

    response = render(request, 'polls/index.html', {
        'questions': questions,
        'selected_choices': selected_choices,
        'text_answers': text_answers,
        'exam_completed': request.session.get('exam_completed', False),
        'exam_code': exam_code_obj,  # truyền object
    })

    # Chặn cache trình duyệt
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response



@never_cache
def submit_exam(request, exam_code):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        supplier_company = request.POST.get('supplier_company', '').strip()
        license_plate = request.POST.get('license_plate', '').strip()
        exam_code = request.POST.get('exam_code')
        exam_code_obj = get_object_or_404(ExamCode, code=exam_code)
        if not exam_code:
            # Nếu không có exam_code thì redirect về trang home hoặc trang khác hợp lý
            return redirect('polls:home')
        if not username or not email:
            return render(request, 'polls/index.html', {
                'questions': Question.objects.all(),
                'selected_choices': request.session.get('selected_choices', {}),
                'text_answers': request.session.get('text_answers', {}),
                'error_message': 'Vui lòng nhập đầy đủ tên và email.'
            })      
        questions = exam_code_obj.questions.all().order_by('question_text')
        score = 0
        score = round(score, 1)  # Làm tròn điểm số
        results = []
        for question in questions:
            field_name = f'question_{question.id}'
            if question.question_type == 'TEXT':
                answer_text = request.POST.get(field_name, '').strip()
                is_correct = False
                text_score = 0
                if question.correct_answer: # câu có đáp án cố định
                    is_correct = (question.correct_answer.strip().lower() == answer_text.lower())
                    text_score = question.max_score if is_correct else 0

                elif answer_text: # Dạng mở (áp dụng NLTK)
                    text_score = score_open_ended_answer(answer_text, question)
                score += text_score

                results.append({
                    'exam_code': exam_code,
                    'question': question.question_text,
                    'selected': answer_text if answer_text else 'Không trả lời',
                    'correct_answer': question.correct_answer,
                    'question_type': 'TEXT',
                    'is_correct': is_correct
                })
            else: # Câu hỏi dạng trắc nghiệm
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
        
        passed = score >= 5
        try:
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
        except IntegrityError:
            return redirect('polls:result', exam_code=exam_code)
        request.session['exam_completed'] = True
        request.session['exam_date'] = datetime.now().strftime('%Y-%m-%d')
        request.session['email'] = email
        request.session['username'] = username
        request.session.modified = True
        return redirect('polls:result', exam_code=exam_code)
    return redirect('polls:index', exam_code=exam_code)

@never_cache
def result(request, exam_code):
    email = request.session.get('email', '')
    results = []         # <== thêm mặc định
    score = 0
    username = 'Người dùng'
    passed = False
    if email and ExamResult.objects.filter(email=email).exists() and not results:
        exam_result = get_object_or_404(ExamResult, email=email)
        results = exam_result.results
        score = round(exam_result.score, 1)
        username = exam_result.username
        passed = exam_result.passed

    # Lọc theo exam_code (Lưu ý kiểu dữ liệu: exam_code trong session có thể là str hoặc int)
    filtered_results = [r for r in results if str(r.get('exam_code')) == str(exam_code)]

    return render(request, 'polls/result.html', {
        'score': score,
        'results': filtered_results,  # Dùng filtered_results thay vì results gốc
        'username': username,
        'passed': passed
    })



def loaderio_verification(request):
    return HttpResponse("loaderio-d62c75f95bb592331c05c414e7ba073a", content_type="text/plain")