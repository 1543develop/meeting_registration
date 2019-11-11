from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import ContactForm, TeacherChoiceForm


def registration(request):
    TeacherChoiceFormSet = formset_factory(TeacherChoiceForm, extra=1)
    if request.method == "POST":
        contact_form = ContactForm(request.POST, prefix="contacts")
        teacher_choice_form_set = TeacherChoiceFormSet(request.POST, prefix="teachers")
        a = contact_form.is_valid()
        b = teacher_choice_form_set.is_valid()
        a = contact_form.cleaned_data
        b = teacher_choice_form_set.cleaned_data
        if contact_form.is_valid() and teacher_choice_form_set.is_valid():
            return HttpResponseRedirect("/thanks/")
    else:
        contact_form = ContactForm(prefix="contacts")
        teacher_choice_form_set = TeacherChoiceFormSet(prefix="teachers")
    return render(request, "registration_form.html", {"contact_form": contact_form,
                                                      "teacher_choice_form_set": teacher_choice_form_set})
