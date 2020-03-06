from django import forms
from django.forms import ModelForm
from .models import Parent, Appointment, Class

TOTAL_FORM_COUNT = 'TOTAL_FORMS'
INITIAL_FORM_COUNT = 'INITIAL_FORMS'
MIN_NUM_FORM_COUNT = 'MIN_NUM_FORMS'
MAX_NUM_FORM_COUNT = 'MAX_NUM_FORMS'
ORDERING_FIELD_NAME = 'ORDER'
DELETION_FIELD_NAME = 'DELETE'

# default minimum number of forms in a formset
DEFAULT_MIN_NUM = 0

# default maximum number of forms in a formset, to prevent memory exhaustion
DEFAULT_MAX_NUM = 1000


class ContactForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['parent_name', 'parent_email', 'student_grade', 'student_name']
        labels = {
            "parent_name": "Имя Родителя",
            "parent_email": "Адрес почты родителя",
            "student_grade": "Класс Ученика",
            "student_name": "Имя Ученика",
        }
        widgets = {
            "parent_name": forms.TextInput(attrs={"class": "form-control",
                                                  "id": "parent_name",
                                                  "placeholder": "Введите ФИО"}),
            "parent_email": forms.EmailInput(attrs={"class": "form-control",
                                                    "id": "parent_email",
                                                    "placeholder": "Введите адрес почты"}),
            "student_grade": forms.TextInput(attrs={"class": "form-control",
                                                    "id": "student_grade",
                                                    "placeholder": "Введите класс"}),
            "student_name": forms.TextInput(attrs={"class": "form-control",
                                                   "id": "student_name",
                                                   "placeholder": "Введите ФИО"}),
        }


class TeacherChoiceForm(forms.Form):
    teacher_name = forms.CharField(label="Имя Учителя", max_length=100,
                                   widget=forms.TextInput(attrs={"class": "form-control teacher_name",
                                                                 "placeholder": "Вводите имя или предмет",
                                                                 "autocomplete": "off"}))

    # comment = forms.CharField(label="Comment")
