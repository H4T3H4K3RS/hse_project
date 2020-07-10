from django import forms

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
