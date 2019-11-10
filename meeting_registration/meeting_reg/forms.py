from django import forms


class ContactForm(forms.Form):
    parent_name = forms.CharField(label="Parent's name", max_length=100)
    parent_email = forms.EmailField(label="Parent's email", max_length=100)
    student_name = forms.CharField(label="Student's name", max_length=100)


class TeacherChoiceForm(forms.Form):
    teacher_name = forms.CharField(label="Teach's name")
    comment = forms.CharField(label="Comment")
