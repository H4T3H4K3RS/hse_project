from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.widgets import PasswordInput, TextInput, EmailInput, URLInput, Textarea


class AccountSignupForm(UserCreationForm):
    username = forms.CharField(
        widget=TextInput(attrs={'class': 'form-control', 'id': 'username'}))
    email = forms.CharField(
        widget=EmailInput(attrs={'class': 'form-control', 'id': 'email'}))
    password1 = forms.CharField(
        widget=PasswordInput(attrs={'class': 'form-control', 'id': 'password1'}))
    password2 = forms.CharField(
        widget=PasswordInput(attrs={'class': 'form-control', 'id': 'password2'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class AccountLoginForm(forms.Form):
    login = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'id': 'login'
        }
    ), required=True)
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'id': 'password'
        }
    ))
