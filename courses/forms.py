from django import forms

from .models import Category, Course, Module, Lesson


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'price', 'thumbnail']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Example: Web Development Fundamentals',
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Describe what students will learn in this course.',
        })
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        self.fields['price'].widget.attrs.update({
            'class': 'form-control',
            'min': 0,
            'step': '0.01',
        })
        self.fields['thumbnail'].widget.attrs.update({'class': 'form-control'})


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['course', 'title', 'order']


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['module', 'title', 'content', 'video_url', 'video_file', 'pdf_attachment', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['module'].widget.attrs.update({'class': 'form-select'})
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Example: Introduction to Django views',
        })
        self.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Add lesson notes, reading instructions, or a short summary.',
        })
        self.fields['video_url'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'https://example.com/lesson-video',
        })
        self.fields['video_file'].widget.attrs.update({'class': 'form-control'})
        self.fields['pdf_attachment'].widget.attrs.update({'class': 'form-control'})
        self.fields['order'].widget.attrs.update({
            'class': 'form-control',
            'min': 0,
        })


class CourseBuilderModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['order'].required = False
        self.fields['order'].initial = 0
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Example: Getting Started',
        })
        self.fields['order'].widget.attrs.update({
            'class': 'form-control',
            'min': 0,
        })


class CourseBuilderLessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_url', 'video_file', 'pdf_attachment', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['order'].required = False
        self.fields['order'].initial = 0
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Example: Course introduction',
        })
        self.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Add lesson notes, instructions, or a short summary.',
        })
        self.fields['video_url'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'https://example.com/lesson-video',
        })
        self.fields['video_file'].widget.attrs.update({'class': 'form-control'})
        self.fields['pdf_attachment'].widget.attrs.update({'class': 'form-control'})
        self.fields['order'].widget.attrs.update({
            'class': 'form-control',
            'min': 0,
        })
