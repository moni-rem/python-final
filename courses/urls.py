from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('course/<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('module/<int:pk>/', views.module_detail, name='module_detail'),
    path('instructor/course/create/', views.create_course, name='create_course'),
    path('instructor/module/create/', views.create_module, name='create_module'),
    path('instructor/lesson/create/', views.create_lesson, name='create_lesson'),
]