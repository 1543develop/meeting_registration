# -*- coding: utf-8 -*-
from json import dumps, loads

from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render

from .forms import ContactForm, TeacherChoiceForm
from .teachers_parser import filter_teachers_by_grade as filter_teachers_by_grade_parser
from .teachers_parser import parse_teachers as teachers_parser
from .teachers_parser import is_valid_grade

data = {
    # each form field data with a proper index form
    'teachers-0-raw': 'my raw field string',

    # form status, number of forms
    'teachers-INITIAL_FORMS': 1,
    'teachers-TOTAL_FORMS': 1,
}


def registration(request):
    TeacherChoiceFormSet = formset_factory(TeacherChoiceForm, extra=1)
    if request.method == "POST":
        contact_form = ContactForm(request.POST, prefix="contacts")
        teacher_choice_form_set = TeacherChoiceFormSet(request.POST, prefix="teachers")
        if contact_form.is_valid() and teacher_choice_form_set.is_valid():
            # contact_form.cleaned_data['parent_name']
            return HttpResponseRedirect("/thanks/")
    else:
        contact_form = ContactForm(prefix="contacts")
        teacher_choice_form_set = TeacherChoiceFormSet(prefix="teachers")
    return render(request, "registration_form.html", {"contact_form": contact_form,
                                                      "teacher_choice_form_set": teacher_choice_form_set})


def give_test_json(request):
    return JsonResponse(loads("""[
    { "id": 1, "name": "Матюхин Виктор Александрович Информатика" },
    { "id": 2, "name": "Amazon AWS" },
    { "id": 3, "name": "Docker" },
    { "id": 4, "name": "Digital Ocean" }
    ]"""), safe=False)


def all_teachers(request):
    answer = [{"name": elem["name"] + " " + elem["subject"]} for elem in teachers_parser()]
    return JsonResponse(answer, safe=False)


def teachers_by_grade(request, grade):
    filtered_teachers = filter_teachers_by_grade_parser(teachers_parser(), grade)
    answer = [{"name": elem["name"] + " " + elem["subject"]} for elem in filtered_teachers]
    return JsonResponse(dumps(answer), safe=False)
