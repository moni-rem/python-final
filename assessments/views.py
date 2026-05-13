from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Quiz, Question, Choice, QuizAttempt, Assignment, AssignmentSubmission
from .forms import QuizForm, QuizAttemptGradeForm, AssignmentForm
from accounts.utils import instructor_required
from accounts.permissions import IsInstructorOrReadOnly
from courses.models import Course, Module
from interactions.utils import sync_course_completion


@login_required
def quiz_list(request):
    modules = Module.objects.select_related('course').order_by(
        'course__title',
        'order',
    )
    selected_module = None
    quizzes = Quiz.objects.none()

    module_id = request.GET.get('module')
    if module_id:
        selected_module = get_object_or_404(modules, pk=module_id)
        quizzes = Quiz.objects.select_related('module', 'module__course').filter(module=selected_module)

    return render(request, 'assessments/quiz_list.html', {
        'modules': modules,
        'selected_module': selected_module,
        'quizzes': quizzes,
    })


@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz.objects.select_related('module', 'module__course'), pk=pk)
    questions = quiz.questions.prefetch_related('choices')
    result = None
    latest_attempt = QuizAttempt.objects.filter(student=request.user, quiz=quiz).order_by('-attempted_at').first()

    if request.method == 'POST':
        score = 0
        total = 0

        # Handle multiple choice scoring if applicable
        if quiz.quiz_type == 'multiple_choice' or quiz.quiz_type == 'mixed':
            mc_questions = questions
            for question in mc_questions:
                total += 1
                selected_choice_id = request.POST.get(str(question.id))
                if selected_choice_id and question.choices.filter(pk=selected_choice_id, is_correct=True).exists():
                    score += 1

        # For essay-only or mixed, score needs manual review
        if quiz.quiz_type == 'essay' or quiz.quiz_type == 'mixed':
            text_response = request.POST.get('text_response')
        else:
            text_response = None

        file_upload = request.FILES.get('file_upload')

        percent = round((score / total) * 100, 2) if total > 0 else 0.0
        needs_review = quiz.quiz_type in ['essay', 'mixed']
        saved_score = percent if quiz.quiz_type == 'multiple_choice' else None

        latest_attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            score=saved_score,
            file_upload=file_upload,
            text_response=text_response
        )
        completion = sync_course_completion(request.user, quiz.module.course, touch_progress=True)
        if completion['certificate_created']:
            messages.success(request, 'Congratulations! Your course certificate is ready.')
        result = {
            'score': saved_score,
            'multiple_choice_score': percent if total > 0 else None,
            'total': total,
            'needs_review': needs_review,
        }

    return render(request, 'assessments/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions,
        'result': result,
        'latest_attempt': latest_attempt,
    })


@login_required
def assignment_list(request):
    assignments = Assignment.objects.select_related('course').all()
    return render(request, 'assessments/assignment_list.html', {'assignments': assignments})


@login_required
@instructor_required
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        form.fields['module'].queryset = Module.objects.filter(course__instructor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz created successfully.')
            return redirect('quiz_list')
    else:
        form = QuizForm()
        form.fields['module'].queryset = Module.objects.filter(course__instructor=request.user)

    return render(request, 'assessments/create_quiz.html', {'form': form})


@login_required
@instructor_required
def review_quiz_attempts(request):
    attempts = QuizAttempt.objects.select_related(
        'student',
        'quiz',
        'quiz__module',
        'quiz__module__course',
    ).order_by('-attempted_at')
    if not (request.user.is_staff or request.user.is_superuser or request.user.role == 'admin'):
        attempts = attempts.filter(quiz__module__course__instructor=request.user)

    pending_attempts = attempts.filter(score__isnull=True).count()
    graded_attempts = attempts.filter(score__isnull=False).count()

    return render(request, 'assessments/review_quiz_attempts.html', {
        'attempts': attempts,
        'pending_attempts': pending_attempts,
        'graded_attempts': graded_attempts,
    })


@login_required
@instructor_required
def grade_quiz_attempt(request, pk):
    attempts = QuizAttempt.objects.select_related(
        'student',
        'quiz',
        'quiz__module',
        'quiz__module__course',
    )
    if not (request.user.is_staff or request.user.is_superuser or request.user.role == 'admin'):
        attempts = attempts.filter(quiz__module__course__instructor=request.user)
    attempt = get_object_or_404(attempts, pk=pk)

    if request.method == 'POST':
        form = QuizAttemptGradeForm(request.POST, instance=attempt)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz attempt has been graded.')
            return redirect('review_quiz_attempts')
    else:
        form = QuizAttemptGradeForm(instance=attempt)

    return render(request, 'assessments/grade_quiz_attempt.html', {
        'attempt': attempt,
        'form': form,
    })


@login_required
@instructor_required
def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        form.fields['course'].queryset = Course.objects.filter(instructor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment created successfully.')
            return redirect('assignment_list')
    else:
        form = AssignmentForm()
        form.fields['course'].queryset = Course.objects.filter(instructor=request.user)

    return render(request, 'assessments/create_assignment.html', {'form': form})


@login_required
def assignment_submit(request, pk):
    assignment = get_object_or_404(Assignment.objects.select_related('course'), pk=pk)
    submission = AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).first()

    if request.method == 'POST':
        file = request.FILES.get('file')
        text_submission = request.POST.get('text_submission', '')

        submission, created = AssignmentSubmission.objects.update_or_create(
            assignment=assignment,
            student=request.user,
            defaults={
                'file': file,
                'text_submission': text_submission,
            }
        )
        completion = sync_course_completion(request.user, assignment.course, touch_progress=True)
        if completion['certificate_created']:
            messages.success(request, 'Your assignment submission has been saved. Your course certificate is ready.')
        else:
            messages.success(request, 'Your assignment submission has been saved.')
        return redirect('assignment_list')

    return render(request, 'assessments/assignment_submit.html', {
        'assignment': assignment,
        'submission': submission,
    })


from rest_framework import viewsets, permissions
from .serializers import (
    QuizSerializer,
    QuestionSerializer,
    ChoiceSerializer,
    QuizAttemptSerializer,
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
)


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.select_related('module').all()
    serializer_class = QuizSerializer
    permission_classes = [IsInstructorOrReadOnly]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('quiz').all()
    serializer_class = QuestionSerializer
    permission_classes = [IsInstructorOrReadOnly]


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.select_related('question').all()
    serializer_class = ChoiceSerializer
    permission_classes = [IsInstructorOrReadOnly]


class QuizAttemptViewSet(viewsets.ModelViewSet):
    queryset = QuizAttempt.objects.select_related('student', 'quiz').all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        attempt = serializer.save(student=self.request.user)
        sync_course_completion(self.request.user, attempt.quiz.module.course, touch_progress=True)

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(student=self.request.user)


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('course').all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsInstructorOrReadOnly]


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.select_related('assignment', 'student').all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        submission = serializer.save(student=self.request.user)
        sync_course_completion(self.request.user, submission.assignment.course, touch_progress=True)

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(student=self.request.user)
