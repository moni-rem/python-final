from django.urls import path

from . import views

urlpatterns = [
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quizzes/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/create/', views.create_quiz, name='create_quiz'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:pk>/submit/', views.assignment_submit, name='assignment_submit'),
]