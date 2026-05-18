from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser, UserProfile


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': 'Choose a username',
            'email': 'you@example.com',
            'first_name': 'First name',
            'last_name': 'Last name',
            'password1': 'Create a password',
            'password2': 'Confirm your password',
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-select' if name == 'role' else 'form-control',
                'placeholder': placeholders.get(name, ''),
            })


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar']


class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    username = forms.CharField(max_length=150, required=False)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=False)

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['username'].initial = self.instance.user.username
            self.fields['role'].initial = self.instance.user.role

        placeholders = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'you@example.com',
            'username': 'Username',
            'bio': 'Write a short introduction about your learning goals, interests, or experience.',
        }

        for name, field in self.fields.items():
            css_class = 'form-select' if name == 'role' else 'form-control'
            if name == 'avatar':
                css_class = 'form-control'

            field.widget.attrs.update({
                'class': css_class,
                'placeholder': placeholders.get(name, ''),
            })

        # Disable role field for non-admin users
        if user and not (user.role == 'admin' or user.is_staff or user.is_superuser):
            self.fields['role'].disabled = True

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', user.first_name)
        user.last_name = self.cleaned_data.get('last_name', user.last_name)
        user.email = self.cleaned_data.get('email', user.email)
        user.username = self.cleaned_data.get('username', user.username)
        user.role = self.cleaned_data.get('role', user.role)
        if commit:
            user.save()
            profile.save()
        return profile
