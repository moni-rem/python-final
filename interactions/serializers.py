from rest_framework import serializers

from .models import UserProgress, Discussion, Comment, Certificate
from courses.models import Lesson


class UserProgressSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)
    completed_lessons = serializers.PrimaryKeyRelatedField(many=True, queryset=Lesson.objects.all())

    class Meta:
        model = UserProgress
        fields = ['id', 'student', 'course', 'completed_lessons', 'last_accessed', 'is_completed']


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    discussion = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'discussion', 'user', 'body', 'created_at']


class DiscussionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Discussion
        fields = ['id', 'course', 'user', 'title', 'body', 'created_at', 'comments']


class CertificateSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Certificate
        fields = ['id', 'student', 'course', 'issued_at', 'certificate_url']
