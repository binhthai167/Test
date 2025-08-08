from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.home, name='home'),
    path('save_name/', views.save_name, name='save_name'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('submit/', views.submit_exam, name='submit_exam'),
    path('result/', views.result, name='result'),
    path('loaderio-d62c75f95bb592331c05c414e7ba073a/', views.loaderio_verification),
] 