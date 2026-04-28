from django.contrib import admin
from .models import UserProgress, Discussion, Comment, Certificate


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'last_accessed', 'is_completed')
    list_filter = ('course', 'is_completed')
    search_fields = ('student__username', 'course__title')


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'user', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'body', 'user__username')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('discussion', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('body', 'user__username')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'issued_at')
    list_filter = ('issued_at',)
    search_fields = ('student__username', 'course__title')
