from django.shortcuts import redirect

class ExamCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/polls/index/' and request.session.get('exam_completed', False):
            return redirect('polls:result')
        return self.get_response(request)