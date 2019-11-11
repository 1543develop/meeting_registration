from django import forms


class ContactForm(forms.Form):
    parent_name = forms.CharField(label="Parent's name", max_length=100,
                                  widget=forms.TextInput(attrs={"class": "form-control",
                                                                "placeholder": "Введите ФИО"}))
    parent_email = forms.EmailField(label="Parent's email", max_length=100,
                                    widget=forms.TextInput(attrs={"class": "form-control",
                                                                  "placeholder": "Введите адрес почты"}))
    student_name = forms.CharField(label="Student's name", max_length=100,
                                   widget=forms.TextInput(attrs={"class": "form-control",
                                                                 "placeholder": "Введите ФИО"}))


class TeacherChoiceForm(forms.Form):
    teacher_name = forms.CharField(label="Teach's name", max_length=100,
                                   widget=forms.TextInput(attrs={"class": "form-control",
                                                                 "placeholder": "Введите ФИО"}))
    # comment = forms.CharField(label="Comment")
