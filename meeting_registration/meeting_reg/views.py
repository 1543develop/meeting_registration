# -*- coding: utf-8 -*-
import logging
import random
import re
import string
from collections import defaultdict
from json import dumps

from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, model_to_dict
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render

from .config import ConfigSecrets
from .email_sender import EmailSender
from .forms import ContactForm, TeacherChoiceForm
from .models import Parent, Teacher, Appointment, Class, OpenDay
from .teachers_parser import filter_teachers_by_class as filter_teachers_by_grade_parser
from .teachers_parser import parse_teachers_schedule

from .tools import beautiful_date, parse_date

cfg = ConfigSecrets()

data = {
    # each form field data with a proper index form
    'teachers-0-raw': 'my raw field string',
    # form status, number of forms
    'teachers-INITIAL_FORMS': 1,
    'teachers-TOTAL_FORMS': 1,
}

logger = logging.getLogger("views")


def get_current_open_day():
    day = OpenDay.objects.filter().first()
    return day


def registration(request):
    day = get_current_open_day()
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
            send_appointments_info_to_email(parent, request)
            return HttpResponseRedirect("thanks")
    else:
        contact_form = ContactForm(prefix="contacts")
        teacher_choice_form_set = TeacherChoiceFormSet(prefix="teachers")
    return render(request, "registration_form.html", {"contact_form": contact_form,
                                                      "teacher_choice_form_set": teacher_choice_form_set,
                                                      "date": beautiful_date(*parse_date(day.date())[:2]),
                                                      "time": day.time(),
                                                      "page_title": "День открытых дверей 1543"})


def re_registration(request, token):
    day = get_current_open_day()
    TeacherChoiceFormSet = formset_factory(TeacherChoiceForm, extra=1)
    if request.method == "POST":
        contact_form = ContactForm(request.POST, prefix="contacts")
        teacher_choice_form_set = TeacherChoiceFormSet(request.POST, prefix="teachers")

        # for form in teacher_choice_form_set:
        #     if form.cleaned_data['teacher_name'].strip() == '':
        #         form.instance.delete()
        #     elif form.cleaned_data:
        #         form.save()

        # new_data = {}
        # for key, val in teacher_choice_form_set.data.items():
        #     print(key)
        #     if re.match(r"teachers-[0-9]+-teacher_name", key):
        #         if val != "":
        #             print(val)
        #             new_data[key] = val
        #     else:
        #         new_data[key] = val
        # teacher_choice_form_set.data = new_data

        if contact_form.is_valid() and teacher_choice_form_set.is_valid():
            backup_form(contact_form.cleaned_data, teacher_choice_form_set.cleaned_data)
            Parent.objects.filter(token=token).delete()
            parent = contact_form.save()
            parent.token = token
            parent.save()
            Appointment.objects.filter(parent=parent).delete()
            add_appointments_to_db(teacher_choice_form_set.cleaned_data, parent)
            send_appointments_info_to_email(parent, request)
            return HttpResponseRedirect("/thanks")
    else:
        parent = Parent.objects.get(token=token)
        contact_form = ContactForm(instance=parent, prefix="contacts")

        initial_data = []
        for appointment in Appointment.objects.filter(parent=parent):
            initial_data.append({"teacher_name": f"{appointment.teacher.name} ({appointment.teacher.subject})"})
        teacher_choice_form_set = TeacherChoiceFormSet(initial=initial_data, prefix="teachers")

    return render(request, "registration_form.html", {"contact_form": contact_form,
                                                      "teacher_choice_form_set": teacher_choice_form_set,
                                                      "date": beautiful_date(*parse_date(day.date())[:2]),
                                                      "time": day.time(),
                                                      "page_title": "День открытых дверей 1543"})


def cancel_application(request, token):
    email_sender = EmailSender(smtp_server_address=cfg["mail"]["stmp_server"],
                               sender_email=cfg["mail"]["email_sender"],
                               password=cfg["mail"]["password"])
    parent = Parent.objects.all().filter(token=token)
    if len(parent) > 0:
        email_sender.send_cancel_application(parent[0], request.build_absolute_uri("/"))
        Appointment.objects.all().filter(parent=parent[0]).delete()
        parent.delete()
        return HttpResponseRedirect("/cancellation")
    else:
        return HttpResponseRedirect("/cancellation_exception")


def cancellation(request):
    return render(request, "cancellation.html")


def cancellation_exception(request):
    return render(request, "cancellation_exception.html")


def send_appointments_info_to_email(parent, request, is_reminder=False):
    email_sender = EmailSender(smtp_server_address=cfg["mail"]["stmp_server"],
                               sender_email=cfg["mail"]["email_sender"],
                               password=cfg["mail"]["password"])
    teacher_list = []
    for appointment in Appointment.objects.filter(parent=parent):
        teacher_list.append(appointment.teacher)
    email_sender.send_alert_to_parent(parent,
                                      teacher_list,
                                      get_current_open_day(),
                                      request.build_absolute_uri(f"/cancel/{parent.token}"),
                                      request.build_absolute_uri(f"/update/{parent.token}"),
                                      is_reminder=is_reminder)


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
    answer = list(sorted([elem.name for elem in Class.objects.all()], key=lambda x: (len(x), x)))
    return JsonResponse(answer, safe=False)


def all_teachers(request):
    answer = defaultdict(list)
    teachers = Teacher.objects.all()
    for teacher in teachers:
        parsed_teacher = f"{teacher.name} ({teacher.subject})"
        answer["all"].append(parsed_teacher)
        for class_ in teacher.classes.all():
            answer[class_.name].append(parsed_teacher)
    return JsonResponse(answer, safe=False)


def teachers_by_grade(request, grade):
    filtered_teachers = filter_teachers_by_grade_parser(parse_teachers_schedule(), grade)
    answer = [f'{elem["name"]} ({elem["subject"].lower()})' for elem in filtered_teachers]
    return JsonResponse(dumps(answer), safe=False)


@login_required
def clear_db(request):
    Teacher.objects.all().delete()
    Parent.objects.all().delete()
    Class.objects.all().delete()
    Appointment.objects.all().delete()
    return HttpResponseRedirect("/panel")


@login_required
def new_day(request):
    Parent.objects.all().delete()
    Appointment.objects.all().delete()
    return HttpResponseRedirect("/panel")


@login_required
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
    return HttpResponseRedirect("/panel")


def create_token(length=20):
    letters_pool = string.ascii_letters
    return "".join(random.choices(letters_pool, k=length))


@login_required
def teacher_mailing(request):
    email_sender = EmailSender(smtp_server_address=cfg["mail"]["stmp_server"],
                               sender_email=cfg["mail"]["email_sender"],
                               password=cfg["mail"]["password"])
    for teacher in Teacher.objects.all():
        parents_list = []
        appointments = Appointment.objects.filter(teacher=teacher)
        for appointment in appointments:
            parents_list.append(model_to_dict(appointment.parent))
        if teacher.email and len(Appointment.objects.filter(teacher=teacher)):
            email_sender.send_alert_to_teacher(model_to_dict(teacher), parents_list, get_current_open_day())
    return HttpResponseRedirect("/panel")


@login_required
def parent_mailing(request):
    for parent in Parent.objects.all():
        send_appointments_info_to_email(parent, request, is_reminder=True)
    return HttpResponseRedirect("/panel")


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


@login_required
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


@login_required
def appointments_dump_for_parent(request):
    dump = defaultdict(list)
    for parent in Parent.objects.all():
        for appointment in Appointment.objects.filter(parent=parent):
            dump[f"{parent.parent_name} ({parent.student_name}, {parent.student_grade})"].append(
                {"name": appointment.teacher.name})
    return HttpResponse(create_html_table_from_parents_dump(dump))


def manip_panel(request):
    return render(request, "panel/manip_panel.html", {"page_title": "Панель управления"})
