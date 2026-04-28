from django import forms

from .models import Category, Course, Module, Lesson


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'price', 'thumbnail']


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['course', 'title', 'order']


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['module', 'title', 'content', 'video_url', 'video_file', 'pdf_attachment', 'order']
