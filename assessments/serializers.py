from rest_framework import serializers

from .models import Quiz, Question, Choice, QuizAttempt, Assignment, AssignmentSubmission


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'question', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'choices']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    module = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'module', 'title', 'description', 'questions']


class QuizAttemptSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    quiz = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'student', 'quiz', 'score', 'attempted_at']


class AssignmentSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'course', 'title', 'description', 'due_date']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    assignment = serializers.StringRelatedField(read_only=True)
    student = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id',
            'assignment',
            'student',
            'file',
            'text_submission',
            'submitted_at',
            'grade',
            'feedback',
        ]
