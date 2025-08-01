from django.db import models
from django import forms

CARGO_TYPE_CHOICES = [
    (1, "Обычный груз"),
    (2, "Хрупкий груз"),
    (3, "Опасный груз"),
]


class DeliveryForm(forms.Form):
    title = forms.CharField(
        label="Название",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите название доставки'
        }),
        error_messages={
            'required': 'Поле "Название" обязательно для заполнения'
        }
    )

    opportunity = forms.FloatField(
        label="Цена",
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        error_messages={
            'required': 'Поле "Цена" обязательно для заполнения',
            'invalid': 'Введите корректную сумму'
        }
    )

    cargo_type = forms.ChoiceField(
        label="Тип посылки",
        choices=CARGO_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        error_messages={
            'required': 'Выберите тип посылки'
        }
    )

    cargo_weight = forms.FloatField(
        label="Вес товара (кг)",
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0.1'
        }),
        error_messages={
            'required': 'Укажите вес товара',
            'invalid': 'Введите корректный вес'
        }
    )

class Delivery():
    @classmethod
    def add_fields(cls, but):
        try:
            existing_fields = but.call_api_method("crm.deal.userfield.list")['result']
            has_weight = any(f['FIELD_NAME'] == 'UF_CRM_CARGO_WEIGHT' for f in existing_fields)
            has_type = any(f['FIELD_NAME'] == 'UF_CRM_CARGO_TYPE' for f in existing_fields)
            if has_weight and has_type:
                return
            field_cargo_type = {
                "USER_TYPE_ID": "enumeration",
                "FIELD_NAME": "CARGO_TYPE",
                "LIST": [
                    {"VALUE": "NORMAL", "SORT" : 1, "DEF" : "Y"},
                    {"VALUE": "FRAGILE", "SORT": 2, "DEF": "N"},
                    {"VALUE": "HAZARDOUS", "SORT": 3, "DEF": "N"},
                ]
            }
            field_cargo_weight = {
                "USER_TYPE_ID": "double",
                "FIELD_NAME": "CARGO_WEIGHT"

            }
            but.call_api_method("crm.deal.userfield.add", field_cargo_type)
            but.call_api_method("crm.deal.userfield.add", field_cargo_weight)

        except Exception as e:
            print(f"Failed to add fields: {e}")
            raise

    @classmethod
    def get_10_delivery_list(cls, but):

        return but.call_api_method("crm.deal.list",
           {
               "select": [
                   'ID',
                   'TITLE',
                   'STAGE_ID',
                   #'CURRENCY_ID',
                   'OPPORTUNITY',
                   'UF_CRM_CARGO_WEIGHT',
                   'UF_CRM_CARGO_TYPE'
               ],
               "order": {
                    "DATE_CREATE": 'DESC',
                },
               "total": 10,
           }
        )['result'][:10]

    @classmethod
    def add_delivery(cls, but, deliveryForm):
        print(deliveryForm.get('title'))
        data_to_add = {
            "TITLE": deliveryForm.get('title'),
            "OPPORTUNITY": deliveryForm.get('opportunity'),
            "STAGE_ID": "C1:NEW",
            "UF_CRM_CARGO_WEIGHT": deliveryForm.get('cargo_weight'),
            "UF_CRM_CARGO_TYPE": deliveryForm.get('cargo_type')
        };
        but.call_api_method("crm.deal.add",
            {
                'fields': data_to_add
            }
        )