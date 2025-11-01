from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('create/', views.quiz_create, name='quiz_create'),
    path('<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('<int:pk>/attempt/', views.quiz_attempt, name='quiz_attempt'),
    path('attempt/<int:attempt_pk>/results/', views.quiz_results, name='quiz_results'),
    path('history/', views.quiz_history, name='quiz_history'),
    path('moderation/', views.quiz_moderation_list, name='quiz_moderation_list'),
    path('<int:pk>/approve/', views.approve_quiz, name='approve_quiz'),
    path('<int:pk>/reject/', views.reject_quiz, name='reject_quiz'),
]

