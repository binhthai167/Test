from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.home, name='home'),
    path('save_userInfor/', views.save_userInfo, name='save_userInfo'),

    path('index/<str:exam_code>', views.index, name='index'),
    path('choice/save/', views.save_choice, name='save_choice'),
    path('save_text_answer/', views.save_text_answer, name='save_text_answer'),

    path('polls/<str:exam_code>/submit/', views.submit_exam, name='submit_exam'),
    path('polls/<str:exam_code>/result/', views.result, name='result'),

    path('polls/<str:exam_code>/', views.start_exam, name='start_exam'),
    path('loaderio-d62c75f95bb592331c05c414e7ba073a/', views.loaderio_verification),
] 