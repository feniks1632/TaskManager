from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'due_date', 'assignee']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'description': forms.Textarea(attrs={'rows': 4}), 
        }

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Обязательно. Потребуется для получения уведомлений."
    )

    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Укажите ваше имя.(необязательно к заполнению)'
    )

    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Укажите ваше имя.(необязательно к заполнению)'
    )


    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user