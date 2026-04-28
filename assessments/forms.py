from django import forms

from .models import Quiz, Assignment


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['module', 'title', 'description']


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['course', 'title', 'description', 'due_date']
