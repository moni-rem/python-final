from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, Assignment, AssignmentSubmission


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'module')
    search_fields = ('title', 'module__title')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    search_fields = ('text', 'quiz__title')


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text', 'question__text')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'attempted_at')
    list_filter = ('attempted_at',)
    search_fields = ('student__username', 'quiz__title')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date')
    list_filter = ('course', 'due_date')
    search_fields = ('title', 'course__title')


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'grade')
    list_filter = ('submitted_at', 'grade')
    search_fields = ('assignment__title', 'student__username')
