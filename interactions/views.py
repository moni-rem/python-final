from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Discussion, Comment, Certificate, UserProgress
from courses.models import Course
from accounts.utils import instructor_required


def discussion_list(request):
    discussions = Discussion.objects.select_related('course', 'user').all()
    return render(request, 'interactions/discussion_list.html', {'discussions': discussions})


def discussion_detail(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    comments = discussion.comments.select_related('user').all()
    return render(request, 'interactions/discussion_detail.html', {
        'discussion': discussion,
        'comments': comments,
    })


@login_required
def create_discussion(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        course_id = request.POST.get('course')
        course = get_object_or_404(Course, pk=course_id)

        if title and body:
            Discussion.objects.create(course=course, user=request.user, title=title, body=body)
            messages.success(request, 'Discussion thread created.')
            return redirect('discussion_list')
        messages.error(request, 'Please provide both a title and a message.')

    courses = Course.objects.all()
    return render(request, 'interactions/create_discussion.html', {'courses': courses})


@login_required
def add_comment(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Comment.objects.create(discussion=discussion, user=request.user, body=body)
            messages.success(request, 'Your comment has been posted.')
        return redirect('discussion_detail', pk=pk)
    return redirect('discussion_detail', pk=pk)


@login_required
def progress_dashboard(request):
    progress_entries = request.user.progress.select_related('course').prefetch_related('completed_lessons').all()
    return render(request, 'interactions/progress.html', {'progress_entries': progress_entries})


@login_required
def certificate_list(request):
    certificates = request.user.certificates.select_related('course').all()
    return render(request, 'interactions/certificate_list.html', {'certificates': certificates})


@login_required
@instructor_required
def monitor_student_progress(request):
    progress_entries = UserProgress.objects.filter(course__instructor=request.user).select_related('student', 'course').prefetch_related('completed_lessons')
    return render(request, 'interactions/instructor_progress.html', {'progress_entries': progress_entries})


from rest_framework import viewsets, permissions
from .serializers import UserProgressSerializer, DiscussionSerializer, CommentSerializer, CertificateSerializer


class UserProgressViewSet(viewsets.ModelViewSet):
    queryset = UserProgress.objects.select_related('student', 'course').prefetch_related('completed_lessons').all()
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(student=self.request.user)


class DiscussionViewSet(viewsets.ModelViewSet):
    queryset = Discussion.objects.select_related('course', 'user').all()
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('discussion', 'user').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.select_related('student', 'course').all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(student=self.request.user)


@login_required
def certificate_list(request):
    certificates = request.user.certificates.select_related('course').all()
    return render(request, 'interactions/certificate_list.html', {'certificates': certificates})
