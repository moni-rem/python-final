import html
import textwrap

from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Discussion, Comment, Certificate, UserProgress
from .utils import sync_course_completion
from assessments.models import QuizAttempt
from courses.models import Course, Enrollment, Lesson
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
    enrollments = request.user.enrollments.select_related('course', 'course__category', 'course__instructor').all()
    progress_cards = []
    summary = {
        'enrolled_courses': 0,
        'completed_courses': 0,
        'completed_lessons': 0,
        'total_lessons': 0,
        'overall_percent': 0,
    }

    for enrollment in enrollments:
        course = enrollment.course
        completion = sync_course_completion(request.user, course)
        progress = completion['progress']
        lesson_total = completion['lesson_total']
        completed_lessons = completion['completed_lessons']
        lesson_percent = round((completed_lessons / lesson_total) * 100) if lesson_total else 0

        quizzes_total = completion['quizzes_total']
        quiz_attempts = QuizAttempt.objects.filter(student=request.user, quiz__module__course=course)
        quizzes_completed = completion['quizzes_completed']
        quiz_percent = round((quizzes_completed / quizzes_total) * 100) if quizzes_total else 0
        average_quiz_score = quiz_attempts.exclude(score__isnull=True).aggregate(Avg('score'))['score__avg']

        assignments_total = completion['assignments_total']
        assignments_submitted = completion['assignments_submitted']
        assignment_percent = round((assignments_submitted / assignments_total) * 100) if assignments_total else 0

        total_items = completion['total_items']
        completed_items = completion['completed_items']
        overall_percent = round((completed_items / total_items) * 100) if total_items else 0
        is_completed = completion['is_completed']

        progress_cards.append({
            'course': course,
            'progress': progress,
            'enrolled_at': enrollment.enrolled_at,
            'lesson_total': lesson_total,
            'completed_lessons': completed_lessons,
            'lesson_percent': lesson_percent,
            'quizzes_total': quizzes_total,
            'quizzes_completed': quizzes_completed,
            'quiz_percent': quiz_percent,
            'average_quiz_score': average_quiz_score,
            'assignments_total': assignments_total,
            'assignments_submitted': assignments_submitted,
            'assignment_percent': assignment_percent,
            'completed_items': completed_items,
            'total_items': total_items,
            'overall_percent': overall_percent,
            'is_completed': is_completed,
        })

        summary['enrolled_courses'] += 1
        summary['completed_courses'] += 1 if is_completed else 0
        summary['completed_lessons'] += completed_lessons
        summary['total_lessons'] += lesson_total

    if progress_cards:
        summary['overall_percent'] = round(
            sum(card['overall_percent'] for card in progress_cards) / len(progress_cards)
        )

    return render(request, 'interactions/progress.html', {
        'progress_cards': progress_cards,
        'summary': summary,
    })


@login_required
@require_POST
def mark_lesson_complete(request, pk):
    lesson = get_object_or_404(Lesson.objects.select_related('module', 'module__course'), pk=pk)
    course = lesson.module.course

    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'Please enroll in this course before tracking lesson progress.')
        return redirect('course_detail', pk=course.pk)

    progress, _ = UserProgress.objects.get_or_create(student=request.user, course=course)
    progress.completed_lessons.add(lesson)

    completion = sync_course_completion(request.user, course, touch_progress=True)

    if completion['certificate_created']:
        messages.success(request, f'Marked "{lesson.title}" as complete. Your certificate is ready.')
    else:
        messages.success(request, f'Marked "{lesson.title}" as complete.')
    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('module_detail', pk=lesson.module.pk)


@login_required
def certificate_list(request):
    certificates = request.user.certificates.select_related('course').all()
    return render(request, 'interactions/certificate_list.html', {'certificates': certificates})


def _svg_text_lines(text, width=34):
    return [html.escape(line) for line in textwrap.wrap(text, width=width)[:2]]


@login_required
def download_certificate(request, pk):
    certificate = get_object_or_404(
        Certificate.objects.select_related('student', 'course'),
        pk=pk,
        student=request.user,
    )
    student_name = certificate.student.get_full_name() or certificate.student.username
    course_title = certificate.course.title
    course_lines = _svg_text_lines(course_title, width=42)
    issued_at = certificate.issued_at.strftime('%b %d, %Y')
    filename = f"certificate-{slugify(course_title)}-{certificate.pk}.svg"

    course_tspans = ''.join(
        f'<tspan x="800" dy="{0 if index == 0 else 30}">{line}</tspan>'
        for index, line in enumerate(course_lines)
    )

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <defs>
    <pattern id="waves" width="90" height="18" patternUnits="userSpaceOnUse">
      <path d="M0 9 Q22.5 0 45 9 T90 9" fill="none" stroke="#e7e7e7" stroke-width="1.5"/>
    </pattern>
    <linearGradient id="gold" x1="0" x2="1">
      <stop offset="0%" stop-color="#f2cf68"/>
      <stop offset="100%" stop-color="#c58b25"/>
    </linearGradient>
  </defs>
  <rect width="1280" height="720" fill="#ffffff"/>
  <rect x="0" y="0" width="1280" height="720" fill="url(#waves)" opacity="0.85"/>
  <rect x="36" y="36" width="1208" height="648" fill="none" stroke="#d8d8d8" stroke-width="1"/>
  <circle cx="-28" cy="360" r="404" fill="#1f376d"/>
  <circle cx="190" cy="360" r="330" fill="none" stroke="url(#gold)" stroke-width="42"/>
  <circle cx="240" cy="360" r="330" fill="#ffffff"/>

  <g fill="#ffffff">
    <text x="88" y="86" font-family="Arial, sans-serif" font-size="20">★</text>
    <text x="124" y="94" font-family="Arial, sans-serif" font-size="28">★</text>
    <text x="166" y="84" font-family="Arial, sans-serif" font-size="18">★</text>
  </g>

  <circle cx="196" cy="478" r="82" fill="url(#gold)"/>
  <circle cx="196" cy="478" r="62" fill="#1f376d"/>
  <text x="196" y="460" text-anchor="middle" fill="#ffffff" font-family="Arial, sans-serif" font-size="18" font-style="italic">Best</text>
  <text x="196" y="488" text-anchor="middle" fill="#ffffff" font-family="Arial, sans-serif" font-size="22" font-weight="700">AWARD</text>
  <text x="196" y="518" text-anchor="middle" fill="#ffffff" font-family="Arial, sans-serif" font-size="16">★ ★ ★</text>

  <text x="800" y="154" text-anchor="middle" fill="#222222" font-family="Arial, sans-serif" font-size="74" letter-spacing="2">CERTIFICATE</text>
  <line x1="596" y1="186" x2="700" y2="186" stroke="#222222" stroke-width="3"/>
  <text x="800" y="192" text-anchor="middle" fill="#444444" font-family="Arial, sans-serif" font-size="20">OF COMPLETION</text>
  <line x1="900" y1="186" x2="1004" y2="186" stroke="#222222" stroke-width="3"/>

  <text x="800" y="286" text-anchor="middle" fill="#222222" font-family="Arial, sans-serif" font-size="26">THIS CERTIFICATE IS PRESENTED TO</text>
  <text x="800" y="374" text-anchor="middle" fill="#222222" font-family="Arial, sans-serif" font-size="56" font-weight="800">{html.escape(student_name).upper()}</text>
  <line x1="502" y1="402" x2="1105" y2="402" stroke="#222222" stroke-width="4"/>

  <text x="800" y="464" text-anchor="middle" fill="#333333" font-family="Arial, sans-serif" font-size="20">For successfully completing the course</text>
  <text x="800" y="496" text-anchor="middle" fill="#1d4ed8" font-family="Arial, sans-serif" font-size="24" font-weight="700">{course_tspans}</text>

  <line x1="520" y1="594" x2="686" y2="594" stroke="#222222" stroke-width="3"/>
  <text x="603" y="626" text-anchor="middle" fill="#222222" font-family="Arial, sans-serif" font-size="20">{html.escape(issued_at)}</text>
  <text x="603" y="654" text-anchor="middle" fill="#666666" font-family="Arial, sans-serif" font-size="18">Date</text>

  <line x1="920" y1="594" x2="1106" y2="594" stroke="#222222" stroke-width="3"/>
  <text x="1013" y="626" text-anchor="middle" fill="#222222" font-family="Arial, sans-serif" font-size="20">E-Learn</text>
  <text x="1013" y="654" text-anchor="middle" fill="#666666" font-family="Arial, sans-serif" font-size="18">Signature</text>
</svg>
"""
    response = HttpResponse(svg, content_type='image/svg+xml')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


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
