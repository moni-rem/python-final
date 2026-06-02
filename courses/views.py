from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.db import transaction

from .models import Category, Course, Module, Lesson, Enrollment
from .forms import CourseBuilderLessonForm, CourseBuilderModuleForm, CourseForm, ModuleForm, LessonForm
from accounts.utils import instructor_required
from accounts.permissions import IsInstructorOrReadOnly
from interactions.models import UserProgress


def home(request):
    featured_courses = Course.objects.select_related('category', 'instructor').order_by('-created_at')[:6]
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'featured_courses': featured_courses,
        'categories': categories,
    })


def course_list(request):
    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    courses = (
        Course.objects.select_related('category', 'instructor')
        .annotate(
            module_count=Count('modules', distinct=True),
            enrollment_count=Count('enrollments', distinct=True),
        )
    )
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(instructor__username__icontains=search_query)
            | Q(instructor__first_name__icontains=search_query)
            | Q(instructor__last_name__icontains=search_query)
        )
    if category_id.isdigit():
        courses = courses.filter(category_id=category_id)
    courses = courses.order_by('-created_at')
    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'module_count': Module.objects.count(),
        'search_query': search_query,
        'selected_category': category_id,
    })


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrolled = False
    if request.user.is_authenticated:
        enrolled = course.enrollments.filter(student=request.user).exists()
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'enrolled': enrolled,
    })


@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    UserProgress.objects.get_or_create(student=request.user, course=course)
    if created:
        messages.success(request, f'You are now enrolled in {course.title}.')
    else:
        messages.info(request, 'You are already enrolled in this course.')
    return redirect('course_detail', pk=course.pk)


def module_detail(request, pk):
    module = get_object_or_404(Module.objects.select_related('course'), pk=pk)
    lessons = module.lessons.all()
    completed_lesson_ids = []
    enrolled = False
    lesson_percent = 0

    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(student=request.user, course=module.course).exists()
        progress = UserProgress.objects.filter(student=request.user, course=module.course).first()
        if progress:
            completed_lesson_ids = list(
                progress.completed_lessons.filter(module=module).values_list('id', flat=True)
            )
            lesson_count = lessons.count()
            lesson_percent = round((len(completed_lesson_ids) / lesson_count) * 100) if lesson_count else 0

    return render(request, 'courses/module_detail.html', {
        'module': module,
        'lessons': lessons,
        'enrolled': enrolled,
        'completed_lesson_ids': completed_lesson_ids,
        'lesson_percent': lesson_percent,
    })


@login_required
@instructor_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        module_form = CourseBuilderModuleForm(request.POST, prefix='module')
        lesson_form = CourseBuilderLessonForm(request.POST, request.FILES, prefix='lesson')

        forms_are_valid = form.is_valid() and module_form.is_valid() and lesson_form.is_valid()
        if forms_are_valid:
            module_title = module_form.cleaned_data.get('title')
            lesson_data = lesson_form.cleaned_data
            has_lesson_content = any([
                lesson_data.get('title'),
                lesson_data.get('content'),
                lesson_data.get('video_url'),
                lesson_data.get('video_file'),
                lesson_data.get('pdf_attachment'),
            ])

            if has_lesson_content and not module_title:
                module_form.add_error('title', 'Add a module title before uploading a lesson.')
                forms_are_valid = False
            if has_lesson_content and not lesson_data.get('title'):
                lesson_form.add_error('title', 'Add a lesson title before uploading lesson content.')
                forms_are_valid = False

        if forms_are_valid:
            with transaction.atomic():
                course = form.save(commit=False)
                course.instructor = request.user
                course.save()

                module = None
                if module_form.cleaned_data.get('title'):
                    module = module_form.save(commit=False)
                    module.course = course
                    module.order = module.order or 0
                    module.save()

                if module and lesson_form.cleaned_data.get('title'):
                    lesson = lesson_form.save(commit=False)
                    lesson.module = module
                    lesson.order = lesson.order or 0
                    lesson.save()

            messages.success(request, 'Course created successfully.')
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm()
        module_form = CourseBuilderModuleForm(prefix='module')
        lesson_form = CourseBuilderLessonForm(prefix='lesson')

    return render(request, 'courses/create_course.html', {
        'form': form,
        'module_form': module_form,
        'lesson_form': lesson_form,
    })


@login_required
@instructor_required
def api_create_course_form(request):
    categories = Category.objects.order_by('name')
    return render(request, 'courses/api_create_course.html', {
        'categories': categories,
    })


@login_required
@instructor_required
def create_module(request):
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        form.fields['course'].queryset = Course.objects.filter(instructor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module created successfully.')
            return redirect('course_list')
    else:
        form = ModuleForm()
        form.fields['course'].queryset = Course.objects.filter(instructor=request.user)

    return render(request, 'courses/create_module.html', {'form': form})


@login_required
@instructor_required
def create_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        form.fields['module'].queryset = Module.objects.filter(course__instructor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson uploaded successfully.')
            return redirect('course_list')
    else:
        form = LessonForm()
        form.fields['module'].queryset = Module.objects.filter(course__instructor=request.user)

    return render(request, 'courses/create_lesson.html', {'form': form})


from rest_framework import viewsets, permissions
from .serializers import CategorySerializer, CourseSerializer, ModuleSerializer, LessonSerializer, EnrollmentSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('category', 'instructor').all()
    serializer_class = CourseSerializer
    permission_classes = [IsInstructorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.select_related('course').all()
    serializer_class = ModuleSerializer
    permission_classes = [IsInstructorOrReadOnly]


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('module').all()
    serializer_class = LessonSerializer
    permission_classes = [IsInstructorOrReadOnly]


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related('student', 'course').all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(student=self.request.user)
