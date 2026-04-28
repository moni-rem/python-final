from rest_framework import serializers

from .models import Category, Course, Module, Lesson, Enrollment


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id',
            'module',
            'title',
            'content',
            'video_url',
            'video_file',
            'pdf_attachment',
            'order',
        ]


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'order', 'lessons']


class CategorySerializer(serializers.ModelSerializer):
    courses = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'courses']


class CourseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    instructor = serializers.StringRelatedField(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'category',
            'instructor',
            'price',
            'thumbnail',
            'created_at',
            'updated_at',
            'modules',
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at']
