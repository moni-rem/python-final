from django.urls import path

from . import views

urlpatterns = [
    path('discussions/', views.discussion_list, name='discussion_list'),
    path('discussions/new/', views.create_discussion, name='create_discussion'),
    path('discussions/<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('discussions/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('progress/', views.progress_dashboard, name='progress_dashboard'),
    path('lessons/<int:pk>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('certificates/', views.certificate_list, name='certificate_list'),
    path('certificates/<int:pk>/download/', views.download_certificate, name='download_certificate'),
    path('instructor/progress/', views.monitor_student_progress, name='monitor_student_progress'),
]
