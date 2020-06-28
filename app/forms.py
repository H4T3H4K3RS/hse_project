from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from django.forms.widgets import PasswordInput, TextInput, EmailInput, URLInput, Textarea
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from app.models import Folder


class FolderChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name}"


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
