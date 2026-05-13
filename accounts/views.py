from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count

from .forms import CustomUserCreationForm, UserProfileForm, UserProfileUpdateForm
from .models import CustomUser, UserProfile
from courses.models import Course, Enrollment
from assessments.models import Quiz, QuizAttempt, Assignment, AssignmentSubmission
from interactions.models import Discussion, Certificate
from .utils import is_instructor_user


def is_admin_user(user):
    return user.is_active and (user.role == 'admin' or user.is_staff or user.is_superuser)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    enrollments = request.user.enrollments.select_related('course')
    progress = request.user.progress.select_related('course')
    certificates = request.user.certificates.select_related('course')

    instructor_context = {}
    if is_instructor_user(request.user):
        instructor_courses = (
            Course.objects.filter(instructor=request.user)
            .select_related('category')
            .annotate(
                enrollment_total=Count('enrollments', distinct=True),
                module_total=Count('modules', distinct=True),
                lesson_total=Count('modules__lessons', distinct=True),
            )
            .order_by('-updated_at')
        )
        instructor_context = {
            'is_instructor_dashboard': True,
            'instructor_courses': instructor_courses,
            'instructor_student_count': Enrollment.objects.filter(course__instructor=request.user).values('student').distinct().count(),
            'instructor_quiz_count': Quiz.objects.filter(module__course__instructor=request.user).count(),
            'instructor_assignment_count': Assignment.objects.filter(course__instructor=request.user).count(),
            'pending_quiz_reviews': QuizAttempt.objects.filter(quiz__module__course__instructor=request.user, score__isnull=True).count(),
            'ungraded_assignment_submissions': AssignmentSubmission.objects.filter(assignment__course__instructor=request.user, grade__isnull=True).count(),
        }

    context = {
        'enrollments': enrollments,
        'progress_list': progress,
        'certificates': certificates,
    }
    context.update(instructor_context)
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileUpdateForm(instance=profile, user=request.user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
    })


@user_passes_test(is_admin_user, login_url='login')
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html', {
        'user_count': CustomUser.objects.count(),
        'course_count': Course.objects.count(),
        'enrollment_count': Enrollment.objects.count(),
        'quiz_count': Quiz.objects.count(),
        'assignment_count': Assignment.objects.count(),
        'discussion_count': Discussion.objects.count(),
        'certificate_count': Certificate.objects.count(),
    })


from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomUserSerializer, UserProfileSerializer


class AdminAnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return Response({
            'user_count': CustomUser.objects.count(),
            'course_count': Course.objects.count(),
            'enrollment_count': Enrollment.objects.count(),
            'quiz_count': Quiz.objects.count(),
            'assignment_count': Assignment.objects.count(),
            'discussion_count': Discussion.objects.count(),
            'certificate_count': Certificate.objects.count(),
        })



class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return super().get_queryset()
        return self.queryset.filter(user=self.request.user)
