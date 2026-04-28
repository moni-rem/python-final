from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Category, Course, Module, Lesson, Enrollment
from .forms import CourseForm, ModuleForm, LessonForm
from accounts.utils import instructor_required
from accounts.permissions import IsInstructorOrReadOnly


def home(request):
    featured_courses = Course.objects.select_related('category', 'instructor').order_by('-created_at')[:6]
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'featured_courses': featured_courses,
        'categories': categories,
    })


def course_list(request):
    courses = Course.objects.select_related('category', 'instructor').all()
    return render(request, 'courses/course_list.html', {'courses': courses})


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
    if created:
        messages.success(request, f'You are now enrolled in {course.title}.')
    else:
        messages.info(request, 'You are already enrolled in this course.')
    return redirect('course_detail', pk=course.pk)


def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    lessons = module.lessons.all()
    return render(request, 'courses/module_detail.html', {
        'module': module,
        'lessons': lessons,
    })


@login_required
@instructor_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully.')
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm()

    return render(request, 'courses/create_course.html', {'form': form})


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
