from django import forms


class ContactForm(forms.Form):
    parent_name = forms.CharField(label="Имя Родителя", max_length=100,
                                  widget=forms.TextInput(attrs={"class": "form-control",
                                                                "placeholder": "Введите ФИО"}))
    parent_email = forms.EmailField(label="Адрес почты родителя", max_length=100,
                                    widget=forms.TextInput(attrs={"class": "form-control",
                                                                  "placeholder": "Введите адрес почты"}))
    student_name = forms.CharField(label="Имя Ученика", max_length=100,
                                   widget=forms.TextInput(attrs={"class": "form-control",
                                                                 "placeholder": "Введите ФИО"}))


class TeacherChoiceForm(forms.Form):
    teacher_name = forms.CharField(label="Имя Учителя", max_length=100,
                                   widget=forms.TextInput(attrs={"class": "form-control",
                                                                 "placeholder": "Введите ФИО"}))
    # comment = forms.CharField(label="Comment")
