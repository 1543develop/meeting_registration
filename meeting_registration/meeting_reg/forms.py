from django import forms


class ContactForm(forms.Form):
    parent_name = forms.CharField(label="Имя Родителя", max_length=100,
                                  widget=forms.TextInput(attrs={"class": "form-control",
                                                                "id": "parent_name",
                                                                "placeholder": "Введите ФИО"}))
    parent_email = forms.EmailField(label="Адрес почты родителя", max_length=100,
                                    widget=forms.TextInput(attrs={"class": "form-control",
                                                                  "id": "parent_email",
                                                                  "placeholder": "Введите адрес почты"}))
    student_grade = forms.CharField(label="Класс Ученика", max_length=100,
                                    widget=forms.TextInput(attrs={"class": "form-control",
                                                                  "id": "student_grade",
                                                                  "placeholder": "Введите класс"}))
    student_name = forms.CharField(label="Имя Ученика", max_length=100,
                                   widget=forms.TextInput(attrs={"class": "form-control",
                                                                 "id": "student_name",
                                                                 "placeholder": "Введите ФИО"}))


class TeacherChoiceForm(forms.Form):
    teacher_name = forms.CharField(label="Имя Учителя", max_length=100,
                                   widget=forms.TextInput(attrs={"class": "form-control teacher_name",
                                                                 "placeholder": "Вводите имя или предмет",
                                                                 "autocomplete": "off"}))
    # comment = forms.CharField(label="Comment")
