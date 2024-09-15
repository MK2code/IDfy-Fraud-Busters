from django import forms
from django.contrib.auth.models import User
from .models import Folder

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class FileUploadForm(forms.Form):
    file_type = forms.ChoiceField(
        choices=[('text', 'Text'), ('pdf', 'PDF'), ('excel', 'Excel')],
        required=True,
        label="Select file type"
    )
    file = MultipleFileField(label='Select files')
    folder = forms.ModelChoiceField(queryset=None, required=False, label="Select an existing folder")
    new_folder_name = forms.CharField(max_length=255, required=False, label='Or create a new folder')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Handle cases where the user is not provided or is anonymous
        if user is None or not isinstance(user, User):
            self.fields['folder'].queryset = Folder.objects.all()  # Show all folders, or filter by other logic
        else:
            self.fields['folder'].queryset = Folder.objects.filter(owner=user)

        self.fields['folder'].choices = [(folder.id, folder.name) for folder in self.fields['folder'].queryset]
