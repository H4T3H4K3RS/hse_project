from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from django.forms.widgets import PasswordInput, TextInput, EmailInput, URLInput, Textarea
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from app.models import Folder


class AccountSignupForm(UserCreationForm):
    username = forms.CharField(label="Имя пользователя",
                               widget=TextInput(attrs={'id': 'username'}))
    email = forms.CharField(label="Электронная Почта",
                            widget=EmailInput(attrs={'id': 'email'}))
    password1 = forms.CharField(label="Пароль",
                                widget=PasswordInput(attrs={'id': 'password1'}))
    password2 = forms.CharField(label="Повторите Пароль",
                                widget=PasswordInput(attrs={'id': 'password2'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class AccountLoginForm(forms.Form):
    login = forms.CharField(label="Имя пользователя/Электронная Почта", widget=forms.TextInput(
        attrs={
            'id': 'login'
        }
    ), required=True)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(
        attrs={
            'id': 'password'
        }
    ))


class AccountNewPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'password1'
            }
        ))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'id': 'password2'
        }
    ), required=True)


class RecoverForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'id': 'email'
            }
        ), required=True
    )
    recaptcha = ReCaptchaField(widget=ReCaptchaWidget(), required=True)
