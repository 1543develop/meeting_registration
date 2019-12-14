# -*- coding: utf-8 -*-
import random
import re
import string
from json import dumps, loads

from django.db.models import QuerySet
from django.forms import formset_factory, model_to_dict
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render

from .config import ConfigSecrets
from .email_sender import EmailSender
from .forms import ContactForm, TeacherChoiceForm
from .models import Parent, Teacher, Appointment
from .teachers_parser import filter_teachers_by_grade as filter_teachers_by_grade_parser
from .teachers_parser import get_names_from_1543ru
from .teachers_parser import parse_teachers as teachers_parser

cfg = ConfigSecrets()

# from .teachers_parser import is_valid_grade

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
            parent = contact_form.save()
            parent.token = create_token()
            parent.save()
            for teacher in filter(lambda x: x, teacher_choice_form_set.cleaned_data):
                teacher = Teacher.objects.get(name=strip_subject(teacher["teacher_name"]))
                app = Appointment.objects.create(teacher=teacher, parent=parent, comment="Nothing")
                app.save()
    else:
        contact_form = ContactForm(prefix="contacts")
        teacher_choice_form_set = TeacherChoiceFormSet(prefix="teachers")
    return render(request, "registration_form.html", {"contact_form": contact_form,
                                                      "teacher_choice_form_set": teacher_choice_form_set})


def re_registration(request, token):
    TeacherChoiceFormSet = formset_factory(TeacherChoiceForm, extra=1)
    if request.method == "POST":
        contact_form = ContactForm(request.POST, prefix="contacts")
        teacher_choice_form_set = TeacherChoiceFormSet(request.POST, prefix="teachers")
        if contact_form.is_valid() and teacher_choice_form_set.is_valid():
            Parent.objects.filter(token=token).delete()
            parent = contact_form.save()
            parent.token = token
            parent.save()
            Appointment.objects.filter(parent=parent).delete()
            for teacher in filter(lambda x: x, teacher_choice_form_set.cleaned_data):
                teacher = Teacher.objects.get(name=strip_subject(teacher["teacher_name"]))
                app = Appointment.objects.create(teacher=teacher, parent=parent, comment="Nothing")
                app.save()
    else:
        parent = Parent.objects.get(token=token)
        contact_form = ContactForm(instance=parent, prefix="contacts")

        initial_data = []
        for appointment in Appointment.objects.filter(parent=parent):
            initial_data.append({"teacher_name": appointment.teacher.name})
        teacher_choice_form_set = TeacherChoiceFormSet(initial=initial_data, prefix="teachers")

    return render(request, "registration_form.html", {"contact_form": contact_form,
                                                         "teacher_choice_form_set": teacher_choice_form_set})


def strip_subject(inp_string):
    return re.sub(r"\([^)]*\)\s*", "", inp_string).strip()


def give_test_json(request):
    return JsonResponse(loads("""[
    { "id": 1, "name": "Матюхин Виктор Александрович Информатика" },
    { "id": 2, "name": "Amazon AWS" },
    { "id": 3, "name": "Docker" },
    { "id": 4, "name": "Digital Ocean" }
    ]"""), safe=False)


def all_teachers(request):
    answer = [{"name": f'{elem["name"]} ({elem["subject"].lower()})'} for elem in teachers_parser()]
    return JsonResponse(answer, safe=False)


def teachers_by_grade(request, grade):
    filtered_teachers = filter_teachers_by_grade_parser(teachers_parser(), grade)
    answer = [{"name": f'{elem["name"]} ({elem["subject"].lower()})'} for elem in filtered_teachers]
    return JsonResponse(dumps(answer), safe=False)


def clear_teachers_from_db(request):
    Teacher.objects.all().delete()


def upload_teachers_to_db(request):
    teachers = get_names_from_1543ru(emails=True)

    for (teacher, email) in teachers:
        Teacher.objects.update_or_create(
            name=teacher,
            email=email
        )
    return HttpResponseRedirect("/admin")


def create_token(length=20):
    letters_pool = string.ascii_letters
    return "".join(random.choices(letters_pool, k=length))


def mailing(request):
    email_sender = EmailSender(smtp_server_address=cfg["mail"]["stmp_server"],
                               sender_email=cfg["mail"]["email_sender"],
                               password=cfg["mail"]["password"])
    for teacher in Teacher.objects.all():
        parents_list = []
        appointments = Appointment.objects.filter(teacher=teacher)
        for appointment in appointments:
            parents_list.append(model_to_dict(appointment.parent))
        email_sender.send_alert_to_teacher(model_to_dict(teacher), parents_list)
    return HttpResponseRedirect("admin")
