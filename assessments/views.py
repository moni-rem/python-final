from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Quiz, Question, Choice, QuizAttempt, Assignment, AssignmentSubmission
from .forms import QuizForm, AssignmentForm
from accounts.utils import instructor_required
from accounts.permissions import IsInstructorOrReadOnly
from courses.models import Course, Module


@login_required
def quiz_list(request):
    quizzes = Quiz.objects.select_related('module', 'module__course').all()
    return render(request, 'assessments/quiz_list.html', {'quizzes': quizzes})


@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.prefetch_related('choices')
    result = None

    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_choice_id = request.POST.get(str(question.id))
            if selected_choice_id and question.choices.filter(pk=selected_choice_id, is_correct=True).exists():
                score += 1

        total = questions.count()
        percent = round((score / total) * 100, 2) if total else 0.0
        QuizAttempt.objects.create(student=request.user, quiz=quiz, score=percent)
        result = {'score': percent, 'total': total}

    return render(request, 'assessments/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions,
        'result': result,
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
    assignment = get_object_or_404(Assignment, pk=pk)
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
        serializer.save(student=self.request.user)

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
        serializer.save(student=self.request.user)

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(student=self.request.user)
