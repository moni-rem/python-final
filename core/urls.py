"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.views import CustomUserViewSet, UserProfileViewSet
from courses.views import CategoryViewSet, CourseViewSet, ModuleViewSet, LessonViewSet, EnrollmentViewSet
from assessments.views import (
    QuizViewSet,
    QuestionViewSet,
    ChoiceViewSet,
    QuizAttemptViewSet,
    AssignmentViewSet,
    AssignmentSubmissionViewSet,
)
from interactions.views import UserProgressViewSet, DiscussionViewSet, CommentViewSet, CertificateViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('profiles', UserProfileViewSet)
router.register('categories', CategoryViewSet)
router.register('courses', CourseViewSet)
router.register('modules', ModuleViewSet)
router.register('lessons', LessonViewSet)
router.register('enrollments', EnrollmentViewSet)
router.register('quizzes', QuizViewSet)
router.register('questions', QuestionViewSet)
router.register('choices', ChoiceViewSet)
router.register('quiz-attempts', QuizAttemptViewSet)
router.register('assignments', AssignmentViewSet)
router.register('submissions', AssignmentSubmissionViewSet)
router.register('progress', UserProgressViewSet)
router.register('discussions', DiscussionViewSet)
router.register('comments', CommentViewSet)
router.register('certificates', CertificateViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('assessments/', include('assessments.urls')),
    path('interactions/', include('interactions.urls')),
    path('', include('courses.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
