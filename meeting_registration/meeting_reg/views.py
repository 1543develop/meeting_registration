from django.shortcuts import render
from .forms import ContactForm, TeacherChoiceForm
from django.http import HttpResponseRedirect
from django.forms import formset_factory


def registration(request):
    teacher_choice_form_set = formset_factory(TeacherChoiceForm)
    if request.method == "POST":
        contact_form = ContactForm(request.POST, prefix="contacts")
        teacher_choice_form_set = teacher_choice_form_set(request.POST, prefix="teachers")
        if contact_form.is_valid() and teacher_choice_form_set.is_valid():
            return HttpResponseRedirect("/thanks/")
    else:
        contact_form = ContactForm(prefix="contacts")
        teacher_choice_form_set = teacher_choice_form_set(prefix="teachers")
    return render(request, "registration_form.html", {"contact_form": contact_form,
                                                      "teacher_choice_form_set": teacher_choice_form_set})
