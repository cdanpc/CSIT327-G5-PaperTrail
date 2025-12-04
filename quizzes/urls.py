from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('create/', views.quiz_create, name='quiz_create'),
    path('<int:pk>/edit/', views.quiz_edit, name='quiz_edit'),
    path('<int:pk>/delete/', views.quiz_delete, name='quiz_delete'),
    path('<int:pk>/bookmark/toggle/', views.toggle_quiz_bookmark, name='toggle_quiz_bookmark'),
    path('<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('<int:pk>/attempt/', views.quiz_attempt, name='quiz_attempt'),
    path('<int:pk>/like/', views.toggle_like, name='like_toggle'),
    path('<int:pk>/rate/', views.rate_quiz, name='rate_quiz'),
    path('<int:pk>/comment/add/', views.add_quiz_comment, name='add_quiz_comment'),
    path('comment/<int:pk>/edit/', views.edit_quiz_comment, name='edit_quiz_comment'),
    path('comment/<int:pk>/delete/', views.delete_quiz_comment, name='delete_quiz_comment'),
    path('attempt/<int:attempt_pk>/results/', views.quiz_results, name='quiz_results'),
    path('history/', views.quiz_history, name='quiz_history'),
    path('moderation/', views.quiz_moderation_list, name='quiz_moderation_list'),
    path('<int:pk>/approve/', views.approve_quiz, name='approve_quiz'),
    path('<int:pk>/reject/', views.reject_quiz, name='reject_quiz'),
    path('<int:pk>/update/', views.update_quiz_details, name='update_quiz_details'),
]

