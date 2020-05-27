from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.widgets import PasswordInput, TextInput, EmailInput, URLInput, Textarea

from app.models import Folder


class FolderChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name}"


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


class LinkAddForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(LinkAddForm, self).__init__(*args, **kwargs)
        self.fields["folder"].queryset = Folder.objects.filter(user=user)

    folder = FolderChoiceField(label="Выберите подборку:", queryset=Folder.objects.none(), to_field_name='name',
                               required=True, empty_label=None)
    link = forms.URLField(label="Ссылка:", initial="https://", widget=forms.TextInput(
            attrs={
                'type': 'url',
                'id': 'url'
            }
        ), required=True)
    # description = forms.CharField(widget=forms.TextInput(
    #     attrs={
    #         'id': 'description'
    #     }
    # ), required=True)


class FolderAddForm(forms.Form):
    name = forms.CharField(label='Название Подборки:', widget=forms.TextInput(
        attrs={
            'id': 'name'
        }
    ), required=True)
    # description = forms.CharField(widget=forms.TextInput(
    #     attrs={
    #         'id': 'description'
    #     }
    # ), required=True)
