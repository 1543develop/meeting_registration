from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import ContactForm, TeacherChoiceForm


# import logging
# logger = logging
def registration(request):
    teacher_choice_form_set = formset_factory(TeacherChoiceForm)
    if request.method == "POST":
        contact_form = ContactForm(request.POST, prefix="contacts")
        teacher_choice_form_set = TeacherChoiceForm(request.POST, prefix="teachers")
        print(contact_form.parent_name)
        if contact_form.is_valid() and teacher_choice_form_set.is_valid():
            print(contact_form, teacher_choice_form_set)
            # return HttpResponseRedirect("/thanks/")
    else:
        contact_form = ContactForm(prefix="contacts")
        teacher_choice_form_set = teacher_choice_form_set(prefix="teachers")
    return render(request, "registration_form.html", {"contact_form": contact_form,
                                                      "teacher_choice_form_set": teacher_choice_form_set})
