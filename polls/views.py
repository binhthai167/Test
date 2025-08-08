from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Choice, Question
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import ExamResult

class IndexView(generic.ListView):
    model = Question
    template_name = 'polls/index.html'
    context_object_name = 'questions'
    def get_queryset(self):
        return Question.objects.all()
def home(request):
    return render(request, 'polls/home.html')
def save_name(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        request.session['username'] = username
        return redirect('polls:index')
    return redirect('polls:home')

def index(request):
    template = 'polls/index.html'
    return render(request, template)

# Create your views here.


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})
    
def submit_exam(request):
    if request.method == 'POST':
        questions = Question.objects.all()
        score = 0
        results = []
        username = request.session.get('username', 'Ẩn danh')
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            try:
                selected_choice = Choice.objects.get(pk=selected_choice_id)
                is_correct = selected_choice.is_correct
                if is_correct:
                    score += 1
                results.append({
                    'question': question,
                    'selected': selected_choice,
                    'is_correct': is_correct
                })
            except:
                results.append({
                    'question': question,
                    'selected': None,
                    'is_correct': False
                })
        passed = score >= 2
        ExamResult.objects.create(username=username, score=score, passed=passed)
        # Lưu kết quả vào session để chuyển sang trang result
        request.session['exam_results'] = [{
            'question': r['question'].question_text,
            'selected': r['selected'].choice_text if r['selected'] else 'Không chọn',
            'is_correct': r['is_correct']
        } for r in results]
        request.session['score'] = score
        request.session['username'] = username
        request.session['passed'] = passed
        return redirect('polls:result')

    return redirect('polls:index')

def result(request):
    results = request.session.get('exam_results', [])
    score = request.session.get('score', 0)
    username = request.session.get('username', 'Người dùng')
    passed = request.session.get('passed', False)
    return render(request, 'polls/result.html', {
        'score': score,
        'results': results,
        'username': username,
        'passed': passed
    })