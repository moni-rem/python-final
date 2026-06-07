
from django.conf import settings
from django.views.static import serve
from django.contrib import admin
from django.urls import path, include, re_path

from core.static_views import serve_static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import CustomUserViewSet, UserProfileViewSet, AdminAnalyticsAPIView
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


@api_view(['GET'])
@permission_classes([AllowAny])
def api_routes(request):
    base_url = request.build_absolute_uri('/api/')
    return Response({
        'auth': {
            'login_token': request.build_absolute_uri('/api/token/'),
            'refresh_token': request.build_absolute_uri('/api/token/refresh/'),
            'browse_api_login': request.build_absolute_uri('/api-auth/login/'),
            'browse_api_logout': request.build_absolute_uri('/api-auth/logout/'),
        },
        'routes': {
            'users': f'{base_url}users/',
            'profiles': f'{base_url}profiles/',
            'categories': f'{base_url}categories/',
            'courses': f'{base_url}courses/',
            'modules': f'{base_url}modules/',
            'lessons': f'{base_url}lessons/',
            'enrollments': f'{base_url}enrollments/',
            'quizzes': f'{base_url}quizzes/',
            'questions': f'{base_url}questions/',
            'choices': f'{base_url}choices/',
            'quiz_attempts': f'{base_url}quiz-attempts/',
            'assignments': f'{base_url}assignments/',
            'submissions': f'{base_url}submissions/',
            'progress': f'{base_url}progress/',
            'discussions': f'{base_url}discussions/',
            'comments': f'{base_url}comments/',
            'certificates': f'{base_url}certificates/',
            'analytics': request.build_absolute_uri('/api/analytics/'),
        },
        'detail_route_format': f'{base_url}<route>/<id>/',
    })


urlpatterns = [
    re_path(r'^static/(?P<path>.*)$', serve_static),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('assessments/', include('assessments.urls')),
    path('interactions/', include('interactions.urls')),
    path('', include('courses.urls')),
    path('api/routes/', api_routes, name='api_routes'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/analytics/', AdminAnalyticsAPIView.as_view(), name='admin_analytics'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Only serve media files locally (not from S3)
if settings.SERVE_MEDIA_FILES and not getattr(settings, 'USE_S3', False):
    urlpatterns += [
        re_path(
            r'^media/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]

    
