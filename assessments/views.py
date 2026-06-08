from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

from .models import Quiz, Question, Choice, QuizAttempt, Assignment, AssignmentSubmission
from .forms import QuizForm, QuizAttemptGradeForm, AssignmentForm, AssignmentSubmissionGradeForm
from accounts.utils import instructor_required, is_instructor_user
from accounts.permissions import IsInstructorOrReadOnly
from courses.models import Category, Course, Enrollment, Module
from interactions.utils import sync_course_completion


DEFAULT_QCM_QUESTION_COUNT = 1
MAX_QCM_QUESTION_COUNT = 50
QCM_CHOICE_COUNT = 4


def _visible_modules_for_user(user):
    modules = Module.objects.select_related('course').order_by(
        'course__title',
        'order',
    )
    if is_instructor_user(user):
        return modules
    return modules.filter(course__enrollments__student=user).distinct()


def _visible_quizzes_for_user(user):
    quizzes = Quiz.objects.select_related('module', 'module__course')
    if is_instructor_user(user):
        return quizzes
    return quizzes.filter(module__course__enrollments__student=user).distinct()


def _visible_assignments_for_user(user):
    assignments = Assignment.objects.select_related('course')
    if is_instructor_user(user):
        return assignments
    return assignments.filter(course__enrollments__student=user).distinct()


def _student_is_enrolled(user, course):
    if is_instructor_user(user):
        return True
    return Enrollment.objects.filter(student=user, course=course).exists()


def _visible_categories_for_user(user):
    categories = Category.objects.order_by('name')
    if is_instructor_user(user):
        return categories.filter(courses__isnull=False).distinct()
    return categories.filter(courses__enrollments__student=user).distinct()


def _get_qcm_question_count(post_data=None):
    if not post_data:
        return DEFAULT_QCM_QUESTION_COUNT

    raw_count = post_data.get('qcm_question_count')
    if raw_count:
        try:
            return min(max(int(raw_count), 1), MAX_QCM_QUESTION_COUNT)
        except ValueError:
            return DEFAULT_QCM_QUESTION_COUNT

    submitted_indexes = []
    for key in post_data.keys():
        if not key.startswith('question_'):
            continue
        parts = key.split('_')
        if len(parts) >= 3 and parts[1].isdigit():
            submitted_indexes.append(int(parts[1]))

    if submitted_indexes:
        return min(max(submitted_indexes) + 1, MAX_QCM_QUESTION_COUNT)
    return DEFAULT_QCM_QUESTION_COUNT

def _build_qcm_form_data(post_data=None):
    question_count = _get_qcm_question_count(post_data)
    questions = []
    for question_index in range(question_count):
        choices = []
        for choice_index in range(QCM_CHOICE_COUNT):
            choices.append({
                'text': post_data.get(f'question_{question_index}_choice_{choice_index}', '') if post_data else '',
                'is_correct': post_data.get(f'question_{question_index}_correct') == str(choice_index) if post_data else False,
            })
        questions.append({
            'text': post_data.get(f'question_{question_index}_text', '') if post_data else '',
            'choices': choices,
        })
    return questions


def _validate_qcm_form_data(qcm_questions):
    errors = []
    valid_questions = []

    for index, question in enumerate(qcm_questions, start=1):
        question_text = question['text'].strip()
        choice_texts = [choice['text'].strip() for choice in question['choices']]
        has_content = bool(question_text or any(choice_texts))

        if not has_content:
            continue

        if not question_text:
            errors.append(f'Question {index} needs question text.')

        filled_choices = [choice_text for choice_text in choice_texts if choice_text]
        if len(filled_choices) < 2:
            errors.append(f'Question {index} needs at least two choices.')

        correct_choice = next((choice for choice in question['choices'] if choice['is_correct']), None)
        if correct_choice is None:
            errors.append(f'Question {index} needs one correct answer.')
        elif not correct_choice['text'].strip():
            errors.append(f'The correct answer for question {index} must have choice text.')

        if question_text and len(filled_choices) >= 2 and correct_choice and correct_choice['text'].strip():
            valid_questions.append(question)

    if not valid_questions:
        errors.append('Add at least one QCM question with choices and a correct answer.')

    return valid_questions, errors


@login_required
def quiz_list(request):
    categories = _visible_categories_for_user(request.user)
    selected_category = None
    category_id = request.GET.get('category')
    modules = _visible_modules_for_user(request.user)
    if category_id:
        selected_category = get_object_or_404(categories, pk=category_id)
        modules = modules.filter(course__category=selected_category)

    selected_module = None
    search_query = request.GET.get('search', '').strip()
    quizzes = _visible_quizzes_for_user(request.user)
    if selected_category:
        quizzes = quizzes.filter(module__course__category=selected_category)

    module_id = request.GET.get('module')
    if module_id:
        selected_module = get_object_or_404(modules, pk=module_id)
        quizzes = quizzes.filter(module=selected_module)
    elif not search_query and not selected_category:
        quizzes = Quiz.objects.none()

    if search_query:
        quizzes = quizzes.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(module__title__icontains=search_query)
            | Q(module__course__title__icontains=search_query)
        )

    return render(request, 'assessments/quiz_list.html', {
        'categories': categories,
        'selected_category': selected_category,
        'modules': modules,
        'selected_module': selected_module,
        'quizzes': quizzes,
        'search_query': search_query,
    })


@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(_visible_quizzes_for_user(request.user), pk=pk)
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
    categories = _visible_categories_for_user(request.user)
    selected_category = None
    category_id = request.GET.get('category')
    assignments = _visible_assignments_for_user(request.user)
    if category_id:
        selected_category = get_object_or_404(categories, pk=category_id)
        assignments = assignments.filter(course__category=selected_category)

    return render(request, 'assessments/assignment_list.html', {
        'assignments': assignments,
        'categories': categories,
        'selected_category': selected_category,
    })


@login_required
def assignment_submissions(request):
    if not is_instructor_user(request.user):
        messages.error(
            request,
            'Only instructors and administrators can access assignment submissions.'
        )
        return redirect('assignment_list')

    q = request.GET.get('q', '').strip()

    submissions = AssignmentSubmission.objects.select_related(
        'assignment',
        'student',
        'assignment__course'
    )

    if not (
        request.user.is_staff or
        request.user.is_superuser or
        request.user.role == 'admin'
    ):
        submissions = submissions.filter(
            assignment__course__instructor=request.user
        )

    if q:
        submissions = submissions.filter(
            Q(student__username__icontains=q) |
            Q(assignment__title__icontains=q) |
            Q(assignment__course__title__icontains=q)
        )

    return render(
        request,
        'assessments/assignment_submissions.html',
        {
            'submissions': submissions,
            'q': q,
        }
    )


@login_required
def grade_assignment_submission(request, pk):
    if not is_instructor_user(request.user):
        messages.error(request, 'Only instructors and administrators can grade assignment submissions.')
        return redirect('assignment_list')

    submissions = AssignmentSubmission.objects.select_related('assignment', 'student', 'assignment__course')
    if not (request.user.is_staff or request.user.is_superuser or request.user.role == 'admin'):
        submissions = submissions.filter(assignment__course__instructor=request.user)

    submission = get_object_or_404(submissions, pk=pk)

    if request.method == 'POST':
        form = AssignmentSubmissionGradeForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Submission updated successfully.')
            return redirect('assignment_submissions')
    else:
        form = AssignmentSubmissionGradeForm(instance=submission)

    return render(request, 'assessments/grade_assignment_submission.html', {
        'submission': submission,
        'form': form,
    })


@login_required
@instructor_required
def create_quiz(request):
    qcm_questions = _build_qcm_form_data()
    qcm_question_count = len(qcm_questions)
    qcm_errors = []

    if request.method == 'POST':
        form = QuizForm(request.POST)
        form.fields['module'].queryset = Module.objects.filter(course__instructor=request.user)
        qcm_questions = _build_qcm_form_data(request.POST)
        qcm_question_count = len(qcm_questions)

        if form.is_valid():
            quiz_type = form.cleaned_data['quiz_type']
            valid_questions = []

            if quiz_type in ['multiple_choice', 'mixed']:
                valid_questions, qcm_errors = _validate_qcm_form_data(qcm_questions)

            if not qcm_errors:
                quiz = form.save()
                for question_data in valid_questions:
                    question = Question.objects.create(
                        quiz=quiz,
                        text=question_data['text'].strip(),
                    )
                    for choice_data in question_data['choices']:
                        choice_text = choice_data['text'].strip()
                        if choice_text:
                            Choice.objects.create(
                                question=question,
                                text=choice_text,
                                is_correct=choice_data['is_correct'],
                            )
                messages.success(request, 'Quiz created successfully.')
                return redirect('quiz_list')
    else:
        form = QuizForm()
        form.fields['module'].queryset = Module.objects.filter(course__instructor=request.user)

    return render(request, 'assessments/create_quiz.html', {
        'form': form,
        'qcm_questions': qcm_questions,
        'qcm_question_count': qcm_question_count,
        'qcm_errors': qcm_errors,
    })


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
    assignment = get_object_or_404(_visible_assignments_for_user(request.user), pk=pk)
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

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset.none()
        if is_instructor_user(self.request.user):
            return self.queryset
        return self.queryset.filter(
            module__course__enrollments__student=self.request.user
        ).distinct()


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('quiz').all()
    serializer_class = QuestionSerializer
    permission_classes = [IsInstructorOrReadOnly]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset.none()
        if is_instructor_user(self.request.user):
            return self.queryset
        return self.queryset.filter(
            quiz__module__course__enrollments__student=self.request.user
        ).distinct()


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.select_related('question').all()
    serializer_class = ChoiceSerializer
    permission_classes = [IsInstructorOrReadOnly]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset.none()
        if is_instructor_user(self.request.user):
            return self.queryset
        return self.queryset.filter(
            question__quiz__module__course__enrollments__student=self.request.user
        ).distinct()


class QuizAttemptViewSet(viewsets.ModelViewSet):
    queryset = QuizAttempt.objects.select_related('student', 'quiz').all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        quiz = serializer.validated_data['quiz']
        if not _student_is_enrolled(self.request.user, quiz.module.course):
            raise PermissionDenied('You must enroll in this course before submitting its quiz.')
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

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset.none()
        if is_instructor_user(self.request.user):
            return self.queryset
        return self.queryset.filter(
            course__enrollments__student=self.request.user
        ).distinct()


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.select_related('assignment', 'student').all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        assignment = serializer.validated_data.get('assignment')
        if assignment and not _student_is_enrolled(self.request.user, assignment.course):
            raise PermissionDenied('You must enroll in this course before submitting its assignment.')
        submission = serializer.save(student=self.request.user)
        sync_course_completion(self.request.user, submission.assignment.course, touch_progress=True)

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(student=self.request.user)
