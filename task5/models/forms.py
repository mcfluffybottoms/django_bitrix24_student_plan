from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django import forms

FILE_TYPE_CHOICES = [
    (1, ".csv"),
    (2, ".xlsx")
]

FILE_EXTENSION_MAP = {
    1: '.csv',
    2: '.xlsx'
}


class UploadFileForm(forms.Form):
    file = forms.FileField(required=False)


class ExportFileForm(forms.Form):
    format = forms.ChoiceField(
        label="Формат экспорта",
        choices=FILE_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        error_messages={
            'required': 'Выберите формат для экспорта'
        }
    )


def get_format_from_form(form):
    choice = form.cleaned_data['format']
    return FILE_EXTENSION_MAP.get(int(choice))
