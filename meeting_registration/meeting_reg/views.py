# -*- coding: utf-8 -*-
import logging
import random
import re
import string
from collections import defaultdict
from json import dumps

from django.forms import formset_factory, model_to_dict
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render

from .config import ConfigSecrets
from .email_sender import EmailSender
from .forms import ContactForm, TeacherChoiceForm
from .models import Parent, Teacher, Appointment, Class
from .teachers_parser import filter_teachers_by_class as filter_teachers_by_grade_parser
from .teachers_parser import parse_teachers_schedule

cfg = ConfigSecrets()

data = {
    # each form field data with a proper index form
    'teachers-0-raw': 'my raw field string',
    # form status, number of forms
    'teachers-INITIAL_FORMS': 1,
    'teachers-TOTAL_FORMS': 1,
}

logger = logging.getLogger("views")


def registration(request):
    TeacherChoiceFormSet = formset_factory(TeacherChoiceForm, extra=1)
    if request.method == "POST":
        contact_form = ContactForm(request.POST, prefix="contacts")
        teacher_choice_form_set = TeacherChoiceFormSet(request.POST, prefix="teachers")
        if contact_form.is_valid() and teacher_choice_form_set.is_valid():
            backup_form(contact_form.cleaned_data, teacher_choice_form_set.cleaned_data)
            parent = contact_form.save()
            parent.token = create_token()
            parent.save()
            add_appointments_to_db(teacher_choice_form_set.cleaned_data, parent)
            send_appointments_info_to_email(parent)
            return HttpResponseRedirect("thanks")
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
            backup_form(contact_form.cleaned_data, teacher_choice_form_set.cleaned_data)
            Parent.objects.filter(token=token).delete()
            parent = contact_form.save()
            parent.token = token
            parent.save()
            Appointment.objects.filter(parent=parent).delete()
            add_appointments_to_db(teacher_choice_form_set.cleaned_data, parent)
            send_appointments_info_to_email(parent)
            return HttpResponseRedirect("/thanks")
    else:
        parent = Parent.objects.get(token=token)
        contact_form = ContactForm(instance=parent, prefix="contacts")

        initial_data = []
        for appointment in Appointment.objects.filter(parent=parent):
            initial_data.append({"teacher_name": appointment.teacher.name})
        teacher_choice_form_set = TeacherChoiceFormSet(initial=initial_data, prefix="teachers")

    return render(request, "registration_form.html", {"contact_form": contact_form,
                                                      "teacher_choice_form_set": teacher_choice_form_set})


def send_appointments_info_to_email(parent):
    email_sender = EmailSender(smtp_server_address=cfg["mail"]["stmp_server"],
                               sender_email=cfg["mail"]["email_sender"],
                               password=cfg["mail"]["password"])
    teacher_list = []
    for appointment in Appointment.objects.filter(parent=parent):
        teacher_list.append(model_to_dict(appointment.teacher))
    email_sender.send_alert_to_parent(model_to_dict(parent), teacher_list)


def add_appointments_to_db(cleaned_teachers_form, parent):
    for teacher in filter(lambda x: x, cleaned_teachers_form):
        try:
            teacher = Teacher.objects.get(name=strip_subject(teacher["teacher_name"]))
            app = Appointment.objects.create(teacher=teacher, parent=parent, comment="Nothing")
            app.save()
        except:
            pass


def backup_form(contact_form: dict, teachers_choice_form: dict):
    with open("forms_backup.txt", "a", encoding="utf-8") as output:
        print(str(contact_form), end=";\n", file=output, flush=False)
        print(str(teachers_choice_form), end=";\n", file=output, flush=False)


def strip_subject(inp_string):
    return re.sub(r"\([^)]*\)\s*", "", inp_string).strip()


def all_classes(request):
    answer = [{"name": elem.name} for elem in Class.objects.all()]
    return JsonResponse(answer, safe=False)


def all_teachers(request):
    answer = defaultdict(list)
    teachers = Teacher.objects.all()
    for teacher in teachers:
        parsed_teacher = {"name": f"{teacher.name} ({teacher.subject})"}
        answer["all"].append(parsed_teacher)
        for class_ in teacher.classes.all():
            answer[class_.name].append(parsed_teacher)
    return JsonResponse(answer, safe=False)


def teachers_by_grade(request, grade):
    filtered_teachers = filter_teachers_by_grade_parser(parse_teachers_schedule(), grade)
    answer = [{"name": f'{elem["name"]} ({elem["subject"].lower()})'} for elem in filtered_teachers]
    return JsonResponse(dumps(answer), safe=False)


def clear_teachers_from_db(request):
    Teacher.objects.all().delete()
    return HttpResponseRedirect("/admin")


def upload_teachers_to_db(request):
    teachers = parse_teachers_schedule()

    for teacher in teachers:

        teacher_obj, _ = Teacher.objects.get_or_create(
            name=teacher["name"],
            email=teacher["email"],
            subject=teacher["subject"],
        )
        teacher_obj.save()
        for class_ in teacher["list_of_classes"]:
            class_obj, _ = Class.objects.get_or_create(name=class_)
            teacher_obj.classes.add(class_obj)
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
        if teacher.email:
            email_sender.send_alert_to_teacher(model_to_dict(teacher), parents_list)
    return HttpResponseRedirect("/admin")


def thanks_page(request):
    return render(request, "thanks.html")


def create_html_table_from_teachers_dump(dump: defaultdict):
    html = """<html><table border="1"><tr><th>Учитель</th><th>Родитель</th></tr>"""
    for (teacher_name, parents) in dump.items():
        html += f"<tr><td>{teacher_name}</td>"
        html += f"<td>"
        for parent in parents:
            html += f"{parent['parent_name']} ({parent['student_name']}, {parent['student_grade']})<br>"
        html += f"</td></tr>"
    html += "</table></html>"
    return html


def appointments_dump_for_teachers(request):
    dump = defaultdict(list)
    for teacher in Teacher.objects.all():
        for appointment in Appointment.objects.filter(teacher=teacher):
            dump[teacher.name].append({"parent_name": appointment.parent.parent_name,
                                       "student_name": appointment.parent.student_name,
                                       "student_grade": appointment.parent.student_grade})
    return HttpResponse(create_html_table_from_teachers_dump(dump))


def create_html_table_from_parents_dump(dump: defaultdict):
    html = """<html><table border="1"><tr><th>Родитель</th><th>Учитель</th></tr>"""
    for (parent_name, teachers) in dump.items():
        html += f"<tr><td>{parent_name}</td>"
        html += f"<td>"
        for teacher in teachers:
            html += f"{teacher['name']}<br>"
        html += f"</td></tr>"
    html += "</table></html>"
    return html


def appointments_dump_for_parent(request):
    dump = defaultdict(list)
    for parent in Parent.objects.all():
        for appointment in Appointment.objects.filter(parent=parent):
            dump[f"{parent.parent_name} ({parent.student_name}, {parent.student_grade})"].append(
                {"name": appointment.teacher.name})
    return HttpResponse(create_html_table_from_parents_dump(dump))
