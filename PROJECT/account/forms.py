from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget
from django.forms.widgets import PasswordInput, TextInput, EmailInput


class SignupForm(UserCreationForm):
    username = forms.CharField(label="Имя пользователя",
                               widget=TextInput(attrs={'id': 'username'}))
    email = forms.CharField(label="Электронная Почта",
                            widget=EmailInput(attrs={'id': 'email'}))
    password1 = forms.CharField(label="Пароль",
                                widget=PasswordInput(attrs={'id': 'password1'}))
    password2 = forms.CharField(label="Повторите Пароль",
                                widget=PasswordInput(attrs={'id': 'password2'}))
    captcha = ReCaptchaField(widget=ReCaptchaWidget(), required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class LoginForm(forms.Form):
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


class NewPasswordForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'id': 'password1'
            }
        ), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'id': 'password2'
        }
    ), required=True)
    user = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                'id': 'user'
            }
        ), required=True
    )
    token = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                'id': 'token'
            }
        ), required=True
    )
    code = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                'id': 'code'
            }
        ), required=True
    )

    class Meta:
        model = User
        fields = ('password1', 'password2')


class RecoverForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'id': 'email'
            }
        ), required=True
    )
    captcha = ReCaptchaField(widget=ReCaptchaWidget(), required=True)


class EditForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'id': 'password1'
            }
        ), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'id': 'password2'
        }
    ), required=False)
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'id': 'username'
            }
        ), required=True
    )

    class Meta:
        model = User
        fields = ('password1', 'password2')
