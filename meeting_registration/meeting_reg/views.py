from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import ContactForm, TeacherChoiceForm

data = {
    # each form field data with a proper index form
    'teachers-0-raw': 'my raw field string',

    # form status, number of forms
    'teachers-INITIAL_FORMS': 1,
    'teachers-TOTAL_FORMS': 2,
}


def registration(request):
    TeacherChoiceFormSet = formset_factory(TeacherChoiceForm, extra=1)
    if request.method == "POST":
        contact_form = ContactForm(request.POST, prefix="contacts")
        teacher_choice_form_set = TeacherChoiceFormSet(request.POST, prefix="teachers")
        if contact_form.is_valid() and teacher_choice_form_set.is_valid():
            return HttpResponseRedirect("/thanks/")
    else:
        contact_form = ContactForm(prefix="contacts")
        teacher_choice_form_set = TeacherChoiceFormSet(prefix="teachers")
    return render(request, "registration_form.html", {"contact_form": contact_form,
                                                      "teacher_choice_form_set": teacher_choice_form_set})
