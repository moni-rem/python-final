from django import forms

from .models import Quiz, QuizAttempt, Assignment


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['module', 'title', 'description', 'quiz_type']
        widgets = {
            'module': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'quiz_type': forms.Select(attrs={'class': 'form-select'}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['course', 'title', 'description', 'due_date']


class QuizAttemptGradeForm(forms.ModelForm):
    class Meta:
        model = QuizAttempt
        fields = ['score', 'feedback']
        widgets = {
            'score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'placeholder': 'Enter score from 0 to 100',
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write feedback for the student',
            }),
        }

    def clean_score(self):
        score = self.cleaned_data.get('score')
        if score is None:
            raise forms.ValidationError('Please enter a score before saving.')
        if score < 0 or score > 100:
            raise forms.ValidationError('Score must be between 0 and 100.')
        return score
