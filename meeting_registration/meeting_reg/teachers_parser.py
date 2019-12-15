# -*- coding: utf-8 -*-
import os

from openpyxl import load_workbook
from django.conf import settings

PATH = os.path.dirname(os.path.realpath(__file__))
SCHEDULE_PATH = PATH + "/teachers_schedule.xlsx"
TEACHERS_NAMES = PATH + "/teachers.txt"


def parse_class_name(class_name):
    num = ""
    class_letters = []
    for letter in class_name:
        if letter.isnumeric():
            num += letter
        elif letter.isalpha():
            class_letters.append(letter)
    return num, class_letters


def all_teacher_full_names(emails=False):
    with open(TEACHERS_NAMES, "r", encoding='utf-8') as file:
        if emails:
            teachers = list(map(lambda str_: str_.strip().split(","), file.readlines()))
        else:
            teachers = list(map(lambda str_: str_.strip().split(",")[0], file.readlines()))
        return teachers


def get_full_name_and_email_by_short_name(short_name):
    full_names = all_teacher_full_names(emails=True)
    for full_name, email in full_names:
        if full_name.split()[0].lower() == short_name.split()[0].lower():
            return full_name, email
    return short_name, ""


def parse_teachers_schedule():
    def get_set_of_classes_in_row(row):
        set_of_classes = set()
        for i in range(3, len(row)):
            if row[i] is None:
                continue
            num, class_letters = parse_class_name(row[i].replace(" ", ""))
            for class_letter in class_letters:
                set_of_classes.add(num + class_letter)
        return set_of_classes

    def parse_row(row):
        set_of_classes = get_set_of_classes_in_row(row)
        short_name = row[1].replace(". ", ".").replace(".", ". ", 1)
        list_of_classes = list(set_of_classes)
        list_of_classes.sort()
        full_name, email = get_full_name_and_email_by_short_name(short_name)
        info = {"name": full_name, "email": email, "subject": row[2],
                "list_of_classes": list_of_classes}
        return info

    wb = load_workbook(SCHEDULE_PATH)
    ws = wb.active

    teachers_list = []
    for row_ in ws.values:
        if row_[0] is None:
            continue
        teachers_list.append(parse_row(row_))

    return teachers_list


def switch_latin_to_cyrillic(string: str):
    return string.replace("A", "А").replace("B", "В")


def filter_teachers_by_class(teachers_list, class_raw):
    class_ = switch_latin_to_cyrillic(class_raw)
    teachers_of_class = []
    for teacher in teachers_list:
        if class_ in teacher["list_of_classes"]:
            teachers_of_class.append(teacher)
    return teachers_of_class


if __name__ == '__main__':
    teachers_ = parse_teachers_schedule()
    print(teachers_)
